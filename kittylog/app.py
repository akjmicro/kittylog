import datetime
from itertools import product

import yaml
from flask import flash, redirect, render_template, request
from wtforms import (
    BooleanField,
    Form,
    IntegerField,
    SelectField,
    SubmitField,
    validators,
)

from kittylog import app
from kittylog.db_access import (
    get_db,
    show_food,
    show_food_sums,
    show_water,
    write_to_food_log,
    write_to_water_log,
    delete_entry,
    change_timestamp,
)


_config = yaml.safe_load(open("config.yml"))


FOOD_ATTRS = {
    "wet_range": ("_wet_grams", "wet grams"),
    "dry_range": ("_dry_grams", "dry grams"),
    "hb_range": ("_hb_treats", "hairball treats"),
    "reg_range": ("_reg_treats", "reg treats"),
}


cats = _config["cats"].keys()
fldnames = [attr[0] for attr in FOOD_ATTRS.values()]


def time_only(timestr):
    return timestr.split(" ")[1].split(".")[0]


class ReusableForm(Form):
    pass


ReusableForm.human = SelectField(
    "Human in charge", choices=[(h, h) for h in _config["humans"]]
)

for cat, food_attr in product(_config["cats"].items(), FOOD_ATTRS.items()):
    if "wet" in food_attr[0]:
        min_range = -int(cat[1]["wet_range"])
        max_range = int(cat[1]["wet_range"])
        magic_numbers = cat[1]["magic_numbers"]
    else:
        min_range = 0
        max_range = int(cat[1][food_attr[0]])
        magic_numbers = []
    setattr(
        ReusableForm,
        cat[0] + food_attr[1][0],
        SelectField(
            cat[0] + " " + food_attr[1][1],
            validators=[validators.required()],
            choices=[
                (str(i), str(i))
                for i in list(range(min_range, 1))
                + magic_numbers
                + list(range(1, max_range))
            ],
            default=0,
            coerce=int,
        ),
    )
ReusableForm.water_given = BooleanField(
    label="<b>Fresh water was given!</b>", default=""
)


@app.route("/", methods=["GET"])
def summary():
    if request.args.get("offset"):
        this_date = (
            datetime.date.today() - datetime.timedelta(int(request.args["offset"]))
        ).isoformat()
    else:
        this_date = datetime.date.today().isoformat()
    headers = ["", "Human", "Kitty", "Wet", "Dry", "# HB", "# Reg", "Delete?"]
    rows = show_food(this_date)
    sum_headers = [
        "Kitty",
        "Total Wet grams",
        "Total Dry grams",
        "Total Hairball treats",
        "Total Regular treats",
    ]
    sum_rows = show_food_sums(this_date)
    water_info = show_water(this_date)[0]
    water_timestamp = water_info["timestamp"]
    water_human = water_info["human"]
    return render_template(
        "summary.html",
        headers=headers,
        rows=rows,
        sum_headers=sum_headers,
        sum_rows=sum_rows,
        this_date=this_date,
        time_only=time_only,
        water_timestamp=water_timestamp,
        water_human=water_human,
    )


@app.route("/entry", methods=["GET", "POST"])
def entry():
    form = ReusableForm(request.form)
    if request.method == "POST" and form.validate:
        nowtime = datetime.datetime.now().isoformat(" ")
        # save the info to the db
        for cat in cats:
            attrs_to_check = [getattr(form, cat + fld).data for fld in fldnames]
            if any(attrs_to_check):
                write_to_food_log(form.human.data, cat, *attrs_to_check)
        if form.water_given.data:
            write_to_water_log(form.human.data)
        return redirect("/")

    return render_template(
        "entry.html", form=form, cats=cats, fldnames=fldnames, getattr=getattr
    )


@app.route("/delete", methods=["POST"])
def delete_entry_page():
    if request.method == "POST":
        print(request.form)
        for delnum in request.form.getlist("do_delete"):
            delete_entry(delnum)
    return redirect("/")


@app.route("/tsedit/<id>/<ts>")
def tsedit(id, ts):
    hour, minute = ts.split(":")
    change_timestamp(id, hour, minute)
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

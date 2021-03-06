import datetime
from itertools import product

from flask import current_app, flash, json, redirect, render_template, request
from wtforms import (
    BooleanField,
    Form,
    IntegerField,
    SelectField,
    SubmitField,
    validators,
)

from kittylog import app, config
from kittylog.db_access import (
    change_timestamp,
    delete_entry,
    get_db,
    get_calorie_data,
    get_calorie_moving_average_data,
    show_food,
    show_food_sums,
    show_human_feeder_stats,
    show_water,
    write_to_food_log,
    write_to_water_log,
)


FOOD_ATTRS = {
    "wet_range": ("_wet_grams", "wet grams"),
    "dry_range": ("_dry_grams", "dry grams"),
    "hb_range": ("_hb_treats", "hairball treats"),
    "reg_range": ("_reg_treats", "reg treats"),
}


cats = config["cats"].keys()
fldnames = [attr[0] for attr in FOOD_ATTRS.values()]


def time_only(timestr):
    return timestr.split(" ")[1].split(".")[0]


class ReusableForm(Form):
    pass


ReusableForm.human = SelectField(
    "Human in charge", choices=[(h, h) for h in config["humans"]]
)

for cat, food_attr in product(config["cats"].items(), FOOD_ATTRS.items()):
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
ReusableForm.water_given = BooleanField(label="Fresh water was given!", default="")


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
    last_water = datetime.datetime.now() - datetime.datetime.fromisoformat(
        water_timestamp
    )
    last_water_secs = last_water.days * 86400 + last_water.seconds
    water_color = "red" if last_water_secs > 86400 else "black"
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
        water_color=water_color,
    )


@app.route("/entry", methods=["GET", "POST"])
def entry():
    current_app.logger.info("In 'entry' view code")
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

    current_app.logger.info("Rendering 'entry' template")
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


#####################
# statistcal views: #
#####################


@app.route("/stats", methods=["GET"])
def graphs():
    offset = request.args.get("offset", "0")
    offset = int(offset)
    rows = show_human_feeder_stats()
    humans = [str(r["human"]) for r in rows]
    counts = [int(r["count"]) for r in rows]
    bindi_calorie_data = get_calorie_data("Bindi", offset)
    bindi_calorie_moving_average_data = get_calorie_moving_average_data("Bindi", offset)
    # turn into template-usable json:
    bindi_calorie_data_json = (
        json.dumps([{"x": i["date"], "y": i["calories"]} for i in bindi_calorie_data])
        .replace('"x"', "x")
        .replace('"y"', "y")
    )
    bindi_calorie_moving_average_data_json = (
        json.dumps(
            [
                {"x": i["date"], "y": i["moving_avg_7"]}
                for i in bindi_calorie_moving_average_data
            ]
        )
        .replace('"x"', "x")
        .replace('"y"', "y")
    )
    return render_template(
        "stats.html",
        Bindi_calorie_data=bindi_calorie_data_json,
        Bindi_calorie_moving_average_data=bindi_calorie_moving_average_data_json,
        humans=humans,
        counts=counts,
    )

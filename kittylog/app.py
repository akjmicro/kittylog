import datetime

from flask import flash, redirect, render_template, request
from wtforms import BooleanField, Form, IntegerField, SelectField, SubmitField, validators

from kittylog import *
from kittylog.db_access import *


def time_only(timestr):
    return timestr.split(' ')[1].split('.')[0]


class ReusableForm(Form):
    feeder = SelectField(
        'Human in charge',
        choices=[(h, h) for h in ['Aaron', 'Amy', 'Annika', 'Sarah']]
    )
    Dos_wet_grams = SelectField(
        'Dos wet grams', validators=[validators.required()],
        choices=[(str(i), str(i)) for i in range(-20, 60)], coerce=int,
        default=0
    )
    Dos_dry_grams = SelectField(
        'Dos dry grams', validators=[validators.required()],
        choices=[(str(i), str(i)) for i in range(0, 54)], coerce=int
    )
    Dos_hb_treats = SelectField(
        'Dos hairball treats', validators=[validators.required()],
        choices=[(str(i), str(i)) for i in range(0, 13)], coerce=int
    )
    Dos_reg_treats = SelectField(
        'Dos regular treats', validators=[validators.required()],
        choices=[(str(i), str(i)) for i in range(0, 24)], coerce=int
    )
    Bindi_wet_grams = SelectField(
        'Bindi wet grams', validators=[validators.required()],
        choices=[(str(i), str(i)) for i in range(-20, 54)], coerce=int,
        default=0
    )
    Bindi_dry_grams = SelectField(
        'Bindi dry grams', validators=[validators.required()],
        choices=[(str(i), str(i)) for i in range(0, 54)], coerce=int
    )
    Bindi_hb_treats = SelectField(
        'Bindi hairball treats', validators=[validators.required()],
        choices=[(str(i), str(i)) for i in range(0, 13)], coerce=int
    )
    Bindi_reg_treats = SelectField(
        'Bindi regular treats', validators=[validators.required()],
        choices=[(str(i), str(i)) for i in range(0, 24)], coerce=int
    )
    water_given = BooleanField(label='<b>Fresh water was given!</b>', default='')


@app.route("/", methods=['GET'])
def summary():
    if request.args.get('offset'):
        this_date = (
            datetime.date.today() - datetime.timedelta(
                int(request.args['offset']))
        ).isoformat()
    else:
        this_date = datetime.date.today().isoformat()
    headers = ['', 'Human', 'Kitty', 'Wet', 'Dry', '# HB', '# Reg', 'Delete?']
    rows = show_log(this_date)
    sum_headers = ['Kitty', 'Total Wet grams', 'Total Dry grams',
                   'Total Hairball treats', 'Total Regular treats']
    sum_rows = show_sums(this_date)
    water_info = show_water(this_date)[0]
    water_timestamp = water_info['timestamp']
    water_feeder = water_info['feeder']
    return render_template(
        'summary.html',
         headers=headers,
         rows=rows,
         sum_headers=sum_headers,
         sum_rows=sum_rows,
         this_date=this_date,
         time_only=time_only,
         water_timestamp=water_timestamp,
         water_feeder=water_feeder
    )


@app.route("/entry", methods=['GET', 'POST'])
def entry():
    form = ReusableForm(request.form)
    if request.method == 'POST' and form.validate:
        nowtime = datetime.datetime.now().isoformat(' ')
        # save the info to the db
        if any([form.Dos_wet_grams.data, form.Dos_dry_grams.data,
                form.Dos_hb_treats.data, form.Dos_reg_treats.data]):
            write_to_food_log(
                form.feeder.data,
                'Dos',
                form.Dos_wet_grams.data, form.Dos_dry_grams.data,
                form.Dos_hb_treats.data, form.Dos_reg_treats.data
            )
        if any([form.Bindi_wet_grams.data, form.Bindi_dry_grams.data,
                form.Bindi_hb_treats.data, form.Bindi_reg_treats.data]):
            write_to_food_log(
                form.feeder.data,
                'Bindi',
                form.Bindi_wet_grams.data, form.Bindi_dry_grams.data,
                form.Bindi_hb_treats.data, form.Bindi_reg_treats.data
            )
        if form.water_given.data:
            write_to_water_log(form.feeder.data)
        return redirect('/')

    return render_template('entry.html', form=form)


@app.route("/delete", methods=['POST'])
def delete_entry_page():
    if request.method == 'POST':
        print(request.form)
        for delnum in request.form.getlist("do_delete"):
            delete_entry(delnum)
    return redirect('/')


@app.route("/tsedit/<id>/<ts>")
def tsedit(id, ts):
    hour, minute = ts.split(':')
    change_timestamp(id, hour, minute)
    return redirect('/')


if __name__ == "__main__":
    app.run()

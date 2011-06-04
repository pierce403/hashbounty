from flask import Flask, render_template, request

from flaskext.wtf import Form, FileField, FieldList, required

class FileUploadForm(Form):

    uploads = FieldList(FileField())


DEBUG = True
SECRET_KEY = 'secret'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route("/", methods=("GET", "POST",))
def index():

    form = FileUploadForm()
    for i in xrange(5):
        form.uploads.append_entry()

    filedata = []

    if form.validate_on_submit():
        for upload in form.uploads.entries:
            filedata.append(upload)

    return render_template("index.html", 
                           form=form, 
                           filedata=filedata)


if __name__ == "__main__":
    app.run()

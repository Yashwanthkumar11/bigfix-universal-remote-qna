from invoke import task

@task
def hi(c, name="Yashwanth"):
    print("Hi {}!".format(name))
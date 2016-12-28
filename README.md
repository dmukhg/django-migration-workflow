# Managing migrations

First, I created this app, using 
`django-admin startproject newness`.

Then, I created the blinkers app using
`python manage.py startapp blinkers`

In the blinkers/models.py, I put the following code
```python
class NewHope(models.Model):
  xml = models.TextField()
  title = models.CharField(max_length=100)
```


## Creating manually-managed tables. `RunSQL`

I let django create the initial migration by running `python manage.py makemigrations`.

This creates a migration that uses django's DDL to create tables. It looks something like this.
```python
class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewHope',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('xml', models.TextField()),
                ('title', models.CharField(max_length=100)),
            ],
        ),
    ]
```

Now, what we want is that the title be extracted automatically by MySQL, so we override the migration file created to look like this.

```python

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.RunSQL(
          """
          --
          -- Create model NewHope
          --
          CREATE TABLE "blinkers_newhope" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
            "xml" text NOT NULL, 
            "title" varchar(100) GENERATED ALWAYS AS (extractvalue(`xml`,'/article/title')) STORED 
          );
          """,
          reverse_sql="BEGIN; DROP TABLE `blinkers_newhope`; COMMIT",
          state_operations=[CreateModel(
            name='NewHope',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('xml', models.TextField()),
                ('title', models.CharField(max_length=100)),
            ],)]
        ),
    ]
```

Note how we are providing the SQL of our own choosing. Additionally, the state_operations field duplicates what the original migration did. This provides django with an understanding of what the operation does.

So now, if you were to run the sqlmigrate command
```bash
$>python manage.py sqlmigrate blinkers 0001_initial                                                             ~/repos/kitchensink/newness
BEGIN;
--
-- Raw SQL operation
--
CREATE TABLE "blinkers_newhope" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "xml" text NOT NULL,
            "title" varchar(100) GENERATED ALWAYS AS (extractvalue(`xml`,'/article/title')) STORED
          );
COMMIT;

```

After this, I added an extra field called fetch in the model. And ran makemigrations, followed by SQL migrate.

```bash
>./manage.py makemigrations blinkers                                                                      ~/repos/kitchensink/newness
>./manage.py sqlmigrate blinkers 0002_newhope_fetch                                                       ~/repos/kitchensink/newness
BEGIN;
--
-- Add field fetch to newhope
--
ALTER TABLE "blinkers_newhope" RENAME TO "blinkers_newhope__old";
CREATE TABLE "blinkers_newhope" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "fetch" integer NOT NULL, "xml" text NOT NULL, "title" varchar(100) NOT NULL);
INSERT INTO "blinkers_newhope" ("xml", "fetch", "id", "title") SELECT "xml", 12, "id", "title" FROM "blinkers_newhope__old";
DROP TABLE "blinkers_newhope__old";
COMMIT;
```

Notice how slyly django dropped the table and created a new one? It does that for _any_ field addition in _any_ model. So, clearly *for any table that we manage on our own with custom SQL, we should continue writing _all_ the migration files ourselves* as described before.

## Dependencies

As long as we use the django makemigrations command to arrive at a Migration file, it will include the dependencies for foreign keys on its own. For example, check out the first few attributes of the  0002_newhope_fetch migration created by django.

```python
class Migration(migrations.Migration):

    dependencies = [
        ('blinkers', '0001_initial'),
    ]
```

So, dependencies within the same app are very well maintained. Let's try out dependencies across apps.

I created a new app (switches) with a new model. This model has a foreign key on a 'blinker' model.

```python
from blinkers.models import NewHope

# Create your models here.
class FarFarAway(models.Model):
  hope = models.ForeignKey(NewHope)
  last = models.IntegerField(default=12)
```

Then the regular, run of the mill:

```shell
> python manage.py makemigrations switches
```

If you look at the generated migration class, this is what you'll find.
```python
class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('blinkers', '0002_newhope_fetch'),
    ]

    operations = [
        migrations.CreateModel(
            name='FarFarAway',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last', models.IntegerField(default=12)),
                ('hope', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blinkers.NewHope')),
            ],
        ),
    ]
```

So it figured out that it depends on blinkers' 0002_newhope_fetch migration which is a good thing. Let's look at sqlmigrate's output. 

```shell
> python manage.py sqlmigrate switches 0001_initial
BEGIN;
--
-- Create model FarFarAway
--
CREATE TABLE "switches_farfaraway" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "last" integer NOT NULL, "hope_id" integer NOT NULL REFERENCES "blinkers_newhope" ("id"));
CREATE INDEX "switches_farfaraway_7b3a55a8" ON "switches_farfaraway" ("hope_id");
COMMIT;
```

Because we don't want to customize the SQL, we can leave this migration as it is.

Then, I changed the default value twice and created migration files using `makemigrations` twice as well. It generated migration files which have correctly aligned dependencies.

## 
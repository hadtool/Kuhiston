from django.db import migrations

VOLUNTEER_PERMISSIONS = [
    # места: волонтёр добавляет/правит свои записи
    ("add_place", "places"),
    ("change_place", "places"),
    ("view_place", "places"),
    ("add_placephoto", "places"),
    ("change_placephoto", "places"),
    ("view_placephoto", "places"),
    # категории и регионы — только просмотр (заводит их админ)
    ("view_placecategory", "places"),
    ("view_region", "places"),
]


def create_volunteer_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    volunteer_group, _ = Group.objects.get_or_create(name="Волонтёр")

    perms = Permission.objects.filter(
        content_type__app_label__in={app for _, app in VOLUNTEER_PERMISSIONS},
        codename__in={code for code, _ in VOLUNTEER_PERMISSIONS},
    )
    volunteer_group.permissions.add(*perms)


def remove_volunteer_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name="Волонтёр").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_volunteer_group, remove_volunteer_group),
    ]
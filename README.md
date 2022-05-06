# allianceauth-pve

[![version](https://img.shields.io/pypi/v/allianceauth_pve.svg)](https://pypi.python.org/pypi/allianceauth_pve)


PvE tool for AllianceAuth


Free software: GNU General Public License v3

Features
========

This package aims at helping groups of people manage PvE sessions, centralized loot management and loot taxes.

Rotations are a sort of containers for entries. When created, they have some options to customize the behavior of the tool with the entries, such as tax rate, count of setups of the system before ratting etc.

Entries are the corrisponding of an actual PvE fleet. They consist in an estimated total loot value and a set of shares.
When an Entry is submitted to a rotation, all the rules of tax rate and setups are applied and the loot value is split between the participants according to their share weight.

When a loot manager sells all the loot, he can close the rotation and enter the actual loot sales value and send money to the people accordingly.

Help wanted
===========

This modeling is based on how whormoles fleets and loot are managed. If you have some feature requests for other types of environment, pls join [AllianceAuth discord](https://discord.gg/fjnHAmk) and give me a shout in the #community-packages channel. I don't have any experience in anything except whormholes so any help is appreciated.

Installation
============

The following is assuming you have a functioning AllianceAuth installation.

1. `pip install allianceauth-pve`.
2. Add `allianceauth_pve` (note the underscore) to your `INSTALLED_APPS`.
3. Run migrations.
4. Run collectstatic.
5. Restart AllianceAuth.


Permissions
===========

The following permissions are provided:
1. `access_pve`: only users with this permission can see the tool and be added in entries.
2. `manage_entries`: only users with this permissions can create entries.
3. `manage_rotations`: only users with this permissions can create and close rotations.

You'll have to assign this permissions to desired groups/states to make the tool working.

Credits
=======

From an original idea of iRBlue.

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.


# allianceauth-pve

[![version](https://img.shields.io/pypi/v/allianceauth_pve.svg)](https://pypi.python.org/pypi/allianceauth_pve)
[![codecov](https://codecov.io/gh/Maestro-Zacht/allianceauth-pve/branch/main/graph/badge.svg?token=STDS7TSGHX)](https://codecov.io/gh/Maestro-Zacht/allianceauth-pve)


PvE tool for AllianceAuth


Free software: GNU General Public License v3

Features
========

This package aims at helping groups of people manage PvE sessions, centralized loot management and loot taxes.

Create a rotation
-----------------

Rotations are a sort of containers for entries. When created, they have some options to customize the behavior of the tool with the entries, such as tax rate, count of setups of the system before ratting etc. 

They can be created by the people with the right permission (see [below](#permissions)). For them, a button will be avaiable in the main page. It'll lead to a form for creating a rotation.


![New Rotation](https://github.com/Maestro-Zacht/allianceauth-pve/raw/main/images/new_rotation.png)


| Field                  | Description                                                                                                                                                                                                   |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name                   |                                                                                                                                                                                                               |
| Priority               | The priority for the rotation in the list of active rotations. Rotations are displayed in descending order of priority.                                                                                       |
| Tax rate               | Tax rate in percentage. 0 for disabling taxes.                                                                                                                                                                |
| Max daily setups       | The maximum number of helped setups a user can get per day. This option is thought for wormholes where you should setup a system before ratting in it. Set to 0 for disabling tracking setups. Defaults to 1. |
| Min people share setup | The minimum number of users in an entry for considering the setups valid. Defaults to 3                                                                                                                       |
| Entry buttons          | [Custom buttons](#buttons-and-roles-setups) to be shown in the Entry forms. You can select them by holding Ctrl and left-clicking. The package comes with buttons for the main C5 and C6 wormhole. sites.     |
| Roles setups           | [Roles presets](#buttons-and-roles-setups) for Entry forms. You can select them by holding Ctrl and left-clicking.                                                                                            |

Add Entries
-----------

Entries are the corrisponding of an actual PvE fleet. They consist in an estimated total loot value and a set of shares.
When an Entry is submitted to a rotation, all the rules of tax rate and setups are applied and the loot value is split between the participants according to their share weight.
To add an entry to a rotation, click on the plus button on the bottom left of the screen.

![Entry Form](https://raw.githubusercontent.com/Maestro-Zacht/allianceauth-pve/main/images/entry_form.png)

Every entry has a list of shares. To add a share, search for the character you want to add in the panel on the right and click the add button.

A share will be added with the first role in the list, 1 site count and no setup. Setups are helpful in wormholes when you want to track who helped setting up a system before ratting. Roles defines how loot will be split between the shares: for example, if someone has 1 site count and a role with a value of 1 and someone else has 1 site count and a role with a value of 2, this last person will receive double the amount of money of the first one.

In order to add a role, you can click on the `New Role` button and create one from scratch or load a roles setup, if you chose at least one in the rotation form, by clicking on the `Load Roles Setup` button.

When you have a role loaded, you can choose it from the dropdown select on the shares.

On the center of the right panel there is the Estimated total section. There is a numeric field and a list of buttons if you selected at least one in the rotation form. you can either input the estimated total by hand or click on the buttons while you are running the sites.

On the right of the Estimated total field there are 4 buttons for incrementing the site count of the shares. If you hover each of them there'll be a tooltip telling what each button does.
The ones that change selected chars only edit the shares with the green arrow. This is helpful if you are doing the form while you are running the sites: if a person leaves, you can click on the arrow and it'll be unselected.

![Selected Shares](https://raw.githubusercontent.com/Maestro-Zacht/allianceauth-pve/main/images/select_button.png)

Once you have submitted the entry, you'll see updating the summary and the entry list on the rotation page. You can edit an entry by clicking the arrow on the right of the row in the entry list and then click on the edit button.

When the loot is sold, a person with the right permission (see [below](#permissions)) can close the rotation and insert the sales value in the form. Then the closed rotation page will be shown with the right amount of money to send to each person, calculated on the sales value.

![Close Rotation Button](https://raw.githubusercontent.com/Maestro-Zacht/allianceauth-pve/main/images/close_rotation.png)

You can see all the closed rotations from the dashboard.

Funding Projects
----------------

In the dashboard, there is a section for funding projects. People with the appropriate permission (see [below](#permissions)) can create projects and add them to the list. When adding entries, an active funding project can be selected with a percentage of the entry to be added to the project. The money will be added to the project total once the rotation is closed.

In each project page, there is a list of the people who have contributed to the project and the total amount of money they have contributed and the current completion percentage of the project.

Projects need to be closed manually by people with the appropriate permission and they will not appear during entry creation.

Closed Rotation
---------------

In a closed rotation summary, you can click on a character name and on an actual total to copy their value. Once you do so, the corresponding row in the table will be of a different color to help tracking down who is already being copied. To reset a row color, click on the `X` button on the right of the row.

Buttons and Roles Setups
------------------------

Buttons and roles setups can be created in the admin page by people who have access.

Settings
--------

| Setting          | Default | Description                                                      |
| ---------------- | ------- | ---------------------------------------------------------------- |
| `PVE_ONLY_MAINS` | `False` | When set to `True`, only main characters are shown in search bar |

Help wanted
===========

This modeling is based on how whormoles fleets and loot are managed. If you have some feature requests for other types of environment, pls join [AllianceAuth discord](https://discord.gg/fjnHAmk) and give me a shout in the #pve-tool channel. I don't have any experience in anything except whormholes so any help is appriciated.

Installation
============

The following is assuming you have a functioning AllianceAuth installation.

1. `pip install allianceauth-pve`
2. Add `allianceauth_pve` (note the underscore) to your `INSTALLED_APPS`
3. Run migrations
4. Run collectstatic
5. Restart AllianceAuth


Updating
========

1. `pip install -U allianceauth-pve`
2. Run migrations
3. Run collectstatic
4. Restart AllianceAuth

Permissions
===========

The following permissions are provided:
1. `access_pve`: only users with this permission can see the tool and be added in entries.
2. `manage_entries`: only users with this permissions can create entries.
3. `manage_rotations`: only users with this permissions can create and close rotations.
4. `manage_funding_projects`: only users with this permissions can create and close funding projects.

You'll have to assign this permissions to desired groups/states to make the tool work.

Credits
=======

From an original idea of iRBlue.

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.


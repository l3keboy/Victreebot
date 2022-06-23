<h1 align="center">Victreebot</h1>
<h2 align="center">The Victreebot Discord bot, a discord bot for Pokémon Go communities.</h2>

<br>

## **Invite Victreebot bot**
This bot is available for invite using the following invite link: <br>
> https://discord.com/api/oauth2/authorize?client_id=927258608234811394&permissions=1506728470775&scope=bot%20applications.commands

There is also an support server available for you to join and **ask questions**, **give feedback** or **just hang-out**!<br>
> https://discord.gg/sVmMUXCYp2

<br>

----

<br>

## **Using Victreebot**
Victreebot utilizes Discords [Slash Commands](https://discord.com/blog/slash-commands-are-here) only! To use these comands, just type <code>/</code> and Discord will automatically prompt you with some commands (Hint: only typing <code>/</code> allows you to explore all slash commands (from all bots) available in the server)<br><br>
Victreebot has the following commands available for you to use:
- <code>/info</code> > Get information about the bots settings and some server stats!
- <code>/trade</code> > Let other people now you are looking to trade a pokémon (Supports **proposing a trade**, **Offering a Pokémon to trade** or **searching for a specified pokémon**)[^1]
- <code>/locations</code> > Add/Delete/Edit a **Gym** or **Pokéstop**, get a list of all **Gyms** or **Pokéstops** or get information about a specific **Gym** or **Pokéstop**
- <code>/pokedex</code> > Get information about a specific **Pokémon**
- <code>/profile {edit/view}</code> > Edit your profile (Your **Friend code(s)** and **active location(s)**) or view some elses profile
- <code>/raid {create/edit/delete}</code> > Create/Edit/Delete a raid
- <code>/reset</code> > Reset Victreebot to the default values (This only resets the emoji's, roles and channels (logs and raids), this does **NOT** reset Victreebot settings!)[^2]
- <code>/setup</code> > Setup Victreebot with the default emoji's, roles and channels[^2]
- <code>/settings update {general/raid/logging}</code> > Update Victreebot's settings[^2]

<br>

----

<br>

## **Submitting issues for Victreebot**
If you encounter any issues, you have some feature requests or have ideas to improve the bot, please let me know! There are two simple ways of getting in contact:
- Join the [Support server](https://discord.gg/sVmMUXCYp2) and chat with me!
- Submit an issue on this repository!

<br>

----

<br>

## **Developing Victreebot**
Victreebot uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html). All changes will be placed in the [CHANGELOG.md](CHANGELOG.md#victreebot-changelog) file<br>
If you want to help the development of Victreebot, there are a few steps involved:
- Read the [CONTRIBUTING.md](CONTRIBUTING.md) guidelines of Victreebot
- Fork the repository. In the repository, make a virtual environment (python -m venv .venv) and enter it (source .venv/bin/activate on Linux, or for Windows use one of .venv\Scripts\activate.ps1, .venv\Scripts\activate.bat, source .venv/Scripts/activate).
- Install  dependencies using <code>pip install -r requirements.txt</code>

After finishing the feature, bugfix or other task, create a merge request and wait!

<br>

----

<br>

## **LICENSE**
This code is developed under the [MIT License](https://opensource.org/licenses/MIT). The license can be found here: [LICENSE](LICENSE)

<br>

----

<br>

[^1]: This is NOT a trading system! This sends an embed with some details so other server members can see the trade in the server!
[^2]: This command can only be executed by users who have the <code>Manage Server</code> permissions!
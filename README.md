# AutoVox Bot

AutoVox is a personal project primarily focused on automatically managing voice channels by dynamically creating and deleting them, as well as assigning default roles. However, that’s just the beginning, as future plans include more advanced features for a streamlined Discord experience.


## Installation

To run AutoVox, you need to have Python 3.10+ and the `py-cord` library installed. Follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/ItsKoga/AutoVox-bot.git
cd AutoVox-bot
```

### 2. install Dependencies
Use `pip` to install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory of the project with the following content:
```
TOKEN = <your-bot-token>

DB_HOST = <your-database-host>
DB_USER = <your-database-user>
DB_PASS = <your-database-password>
DB_NAME = <your-database-name>
```

**TOKEN:** The token for your Discord bot. You can get this from the [Discord Developer Portal](https://discord.com/developers/applications).

### 4. Run the Bot
```bash
python bot.py
```
Make sure the bot is invited to your Discord server with the proper permissions. You can generate an invite link using the Discord Developer Portal.

### Contribution
Feel free to contribute to the project! Please submit a pull request with a detailed description of the changes.

### License
This project is licensed under the MIT License (with modifications). See the [LICENSE file](https://github.com/ItsKoga/AutoVox/blob/main/LICENSE) for details.
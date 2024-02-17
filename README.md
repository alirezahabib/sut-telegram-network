# Telegram Group Network Analysis

![result](plots/network2.jpg)

## Overview

We studied the communication network among members of the course within the Telegram group. Using Telegram’s MTProto API and telethon library, we collected data on users and message interactions. The gathered data was saved in a database for further analysis. We analyzed the degree distribution of individuals interacting, revealing power-law behavior akin to real social networks. 
The network was constructed based on interactions such as replies, reactions, and pinned messages.

## Features

- Utilizes Telegram's MTProto API and Telethon library for data collection.
- Captures and stores user profiles and various message interactions in a database.
- Analyzes the degree distribution of participants engaging in interactions, revealing power-law behavior akin to real social networks.
- Constructs a network framework incorporating interactions such as replies, reactions, and pinned messages, offering insights into network dynamics and participant engagement patterns.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/telegram-group-network.git
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Obtain a personal Telegram client code to access the Telegram API.
2. Configure the Telegram API credentials in the project.
3. Run the data collection script to gather user profiles and message interactions.
4. Analyze the collected data using the provided analysis tools.
5. Visualize the network structure using appropriate visualization libraries.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the creators of Telegram and Telethon for providing robust APIs and libraries for data collection.
- Special thanks to the contributors and maintainers of open-source libraries used in this project.
- Hat tip to the course participants of the course Network Analysis Fall Semester 2023 whose interactions formed the basis of this analysis.

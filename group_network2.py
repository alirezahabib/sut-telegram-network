import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import os


# User and Message classes
class User:
    def __init__(self, user_id: int, username, access_hash, first_name, last_name, group_id: int, group):
        self.user_id = user_id
        self.username = username
        self.access_hash = access_hash,
        self.first_name = first_name
        self.last_name = last_name
        self.group_id = group_id
        self.group = group
        self.profile_pic = None  # Set if a profile picture exists


class Message:
    def __init__(self, message_id: int, from_user_id: int, reply_to: int, pinned: bool, message: str, reactions):
        self.message_id = message_id
        self.from_user_id = from_user_id
        self.reply_to = reply_to
        self.pinned = pinned
        self.message = message
        self.reactions = [int(x) for x in str(reactions).split('-')] if pd.notnull(reactions) else []


# Load data from CSV files
def load_data(group_id):
    members_path = f"database/group-{group_id}/members.csv"
    messages_path = f"database/group-{group_id}/messages.csv"

    members_df = pd.read_csv(members_path)
    messages_df = pd.read_csv(messages_path)

    users = {row['user_id']: User(**row) for _, row in members_df.iterrows()}
    messages = {row['message_id']: Message(**row) for _, row in messages_df.iterrows()}

    profile_pics_path = "database/profile_pics/"
    for user_id in users:
        pic_path = f"{profile_pics_path}{user_id}.jpg"
        if os.path.exists(pic_path):
            users[user_id].profile_pic = pic_path

    return users, messages


# Create the network graph
def create_network(users, messages):
    G = nx.Graph()

    # Add nodes (users)
    for user_id, user in users.items():
        G.add_node(user_id, image=user.profile_pic or 'default.jpg')

    # Function to add or update an edge
    def add_or_update_edge(G, source, target):
        if G.has_edge(source, target):
            # Increase weight if edge exists
            G[source][target]['weight'] += 1
        else:
            # Create new edge with weight 1
            G.add_edge(source, target, weight=1)

    # Add edges based on messages, replies, and reactions
    for message_id, message in messages.items():
        # Messages replying to other messages
        if message.reply_to in messages:
            original_sender_id = messages[message.reply_to].from_user_id
            add_or_update_edge(G, message.from_user_id, original_sender_id)

        # Reactions to messages
        for reacting_user_id in message.reactions:
            add_or_update_edge(G, reacting_user_id, message.from_user_id)

        # Pinned messages
        # if message.pinned:
        #     for user_id in users:
        #         if user_id != message.from_user_id:
        #             add_or_update_edge(G, message.from_user_id, user_id)

    return G


def make_circular(image_path):
    img = Image.open(image_path)
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + img.size, fill=255)
    result = Image.new('RGBA', img.size, (0, 0, 0, 0))
    result.paste(img, (0, 0), mask=mask)
    return result


# Draw the network
def draw_network(G):
    plt.figure(figsize=(16, 9))

    # Calculate node sizes based on in-degree
    degrees = G.degree(weight='weight')
    node_sizes = [np.log(degree + 1) * 130 for _, degree in degrees]  # Apply logarithm and scale
    pos = nx.spring_layout(G, k=3, iterations=50)

    # Draw nodes with sizes based on in-degree
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes)

    # Draw edges with thickness based on weight
    edge_weights = np.array([G[u][v]['weight'] for u, v in G.edges()])
    edge_weights = edge_weights / np.max(edge_weights)

    nx.draw_networkx_edges(G, pos, width=(1 + 3 * edge_weights), alpha=(0.2 + edge_weights * 0.8), node_size=node_sizes)

    # Draw labels
    # nx.draw_networkx_labels(G, pos)

    # Add profile pictures to nodes
    ax = plt.gca()
    fig = plt.gcf()
    trans = ax.transData.transform
    trans2 = fig.transFigure.inverted().transform
    for node in G.nodes():
        path = './database/profile_pics/' + str(node) + '.jpg'
        if os.path.exists(path):
            imsize = np.log(degrees[node] + 1) * 0.02
            (x, y) = pos[node]
            xx, yy = trans((x, y))  # figure coordinates
            xa, ya = trans2((xx, yy))  # axes coordinates
            a = plt.axes((xa - imsize / 2.0, ya - imsize / 2.0, imsize, imsize))
            a.imshow(make_circular(path))
            a.set_aspect('equal')
            a.axis('off')
    # for node in G.nodes:
    #     image_path = 'default.jpg'
    #     image = Image.open(image_path)
    #     ax.imshow(image, extent=(pos[node][0] - 0.01, pos[node][0] + 0.01, pos[node][1] - 0.01, pos[node][1] + 0.01))
    plt.tight_layout()
    plt.savefig('./network.png', dpi=600)
    # plt.show()


def plot_hist(G):
    G.remove_nodes_from(list(nx.isolates(G)))
    degrees = G.degree()
    degrees = [degree for _, degree in degrees]
    plt.hist(degrees, bins=len(degrees) // 2, rwidth=0.93)
    plt.title('Degree Distribution (isolated nodes removed)')
    plt.xlabel('Weighted Degree')
    plt.ylabel('Frequency')
    plt.xscale('log')
    plt.yscale('log')
    plt.savefig('./hist.png', dpi=600)
    plt.show()


import powerlaw

def fit_exponential(G):
    avalanches = [G.degree(node) for node in G.nodes()]
    results = powerlaw.Fit(avalanches, discrete=True, xmin=5)

    plt.figure()
    results.plot_pdf(marker='o', linestyle='None')
    results.power_law.plot_pdf(linestyle='--', ax=plt.gca(), label=f'p ∝ s^-b, b = {results.power_law.alpha:.4f}')

    plt.title(f'Degree Fit')
    plt.xlabel(f'Degree, xmin={results.power_law.xmin:.0f}')
    plt.ylabel('Frequency')
    plt.xscale('linear')
    plt.yscale('linear')
    plt.legend()
    plt.savefig(f'./fit.png', dpi=600)
    #plt.show()

    print('resutls')
    print(f'p(s) ∝ s^-b, s > s_min\n')
    print(f'   b =  {results.power_law.alpha:.4f}')
    print(f'   s_min: {results.power_law.xmin:.0f}')
    print(f'   Kolmogorov-Smirnov statistic: {results.power_law.D:.4f}')

# Load data and create the network
group_id = 1952093821
users, messages = load_data(group_id)
G = create_network(users, messages)
# draw_network(G)
#plot_hist(G)

fit_exponential(G)

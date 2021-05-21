import requests
import json
from tqdm import tqdm
import config

def get_comments(get_comments_api_url, post_id):
    """
        Fetches data from the comments endpoint of an API,
        and returns as python dictionary

        :param get_endpoint_url: url/endpoint of API to be called ; dtype: string
        :return: data fetched from the API endpoint as python dictionary.
    """
    data_not_loaded = True
    while data_not_loaded:
        try:
            url = get_comments_api_url.format(post_id)
            data = requests.get(url)
            data = json.loads(data.content)
            return data
        except Exception as e:
            print(e)
            print("Reconnecting to the sever ...")

def get_data(get_endpoint_url):
    """
        Fetches data from the provided endpoint of an API
        and returns as python dictionary

        :param get_endpoint_url: url/endpoint of API to be called ; dtype: string
        :return: data fetched from the API endpoint as python dictionary.
    """
    data_not_loaded = True
    while data_not_loaded:
        try:
            data = requests.get(get_endpoint_url)
            data = json.loads(data.content)
            return data
        except Exception as e:
            print(e)
            print("Reconnecting to the sever ...")


def loading_users():
    """
    Fetches data from "users" endpoint of our API

    :return: users data fetched from the API endpoint.
    """
    users = get_data(config.api_endpoints["users"])
    return users


def loading_posts():
    """
    Fetches data from "posts" endpoint of our API

    :return: posts data fetched from the API endpoint.
    """
    posts_data = get_data(config.api_endpoints["posts"])
    return posts_data


def loading_comments(post_ids_):
    list_of_comments = []
    for post_id in tqdm(post_ids_,desc="loading comments "):
        comments_fetched = get_comments(config.api_endpoints["comments"], post_id)
        list_of_comments.append(comments_fetched)
    return list_of_comments


def extract_user_ids(users_data_):
    """
    Extracts user_ids from list containing each users details

    :param users_data_: list containing each users details
    :return: list containing users ids.
    """
    user_id_list = [user_['id'] for user_ in users_data_]
    return user_id_list


def extract_post_ids(posts_data_):
    """
        Extracts post_ids from list containing each users details

        :param posts_data_: list containing each post's details
        :return: list containing post ids.
        """
    post_id_list = [post_['id'] for post_ in posts_data_]
    return post_id_list


def link_comments_to_postid(list_of_comments):
    """

    :param list_of_comments:
    :return: dictionary with keys as post_id and values as post's comments
    """
    # creating a dictionary to keep post's comments in link to the post_id
    post_comments_dictionary = {post_id: [] for post_id in post_ids}
    for post in post_comments_dictionary.keys():
        post_comments_dictionary[post] = list_of_comments[post-1]
    return post_comments_dictionary


def link_comments_to_post(post_comments_dict, posts_data_):
    """

    :param post_comments_dict: with post_id as keys and list of post's comments as value
    :param posts_data_: data of all the posts obtained from posts API endpoint
    :return: updated post data with comments included
    """
    for post in posts_data_:
        post_id = post['id']
        comments = post_comments_dict[post_id]
        comments = [{key: value for key, value in comment.items() if key != 'postId'} for comment in comments]
        post['comments'] = comments
    return posts_data_


def link_posts_to_users_id(posts_with_comments):
    """

    :param posts_with_comments:
    :return: dictionary with user_id as keys and list of user's posts as value
    """
    # creating a dictionary to keep user's post in link to the user_id
    user_posts_dictionary = {k: [] for k in user_ids}
    for post in posts_with_comments:
        userid = post['userId']
        post = {key: value for key, value in post.items() if key != 'userId'}
        user_posts_dictionary[userid].append(post)
    return user_posts_dictionary


def link_posts_to_users(user_posts_dict, users_data_):
    """

    :param user_posts_dict: with key as user_id and value as list of user's posts
    :param users_data_: user data fetched from user_API
    :return: updated user_data with posts list added to each user.
    """
    for user in users_data_:
        user_id = user['id']
        if user_id in user_posts_dict.keys():
            user['posts'] = user_posts_dict[user_id]
    return users_data_


if __name__ == '__main__':

    users_data = loading_users()
    posts_data = loading_posts()

    user_ids = extract_user_ids(users_data)

    # creating a dictionary to keep user's post and comments in link to the user_id

    post_ids = extract_post_ids(posts_data)

    comments_data = loading_comments(post_ids)

    post_id_with_comments = link_comments_to_postid(comments_data)

    post_with_comments = link_comments_to_post(post_id_with_comments, posts_data)

    user_id_with_posts = link_posts_to_users_id(post_with_comments)

    user_with_posts = link_posts_to_users(user_id_with_posts, users_data)

    with open('data.json', 'w') as outfile:
        json.dump(users_data, outfile)
    outfile.close()














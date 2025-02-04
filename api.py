import requests
import argparse


username = 'priyanshuexpense'
token = '16740e53abe59588a59237c40e366296479907cd'

base_url = "https://www.pythonanywhere.com"
path = ""

endpoints = {
    "cpu": {"url": f"/api/v0/user/{username}/cpu/", "allowed_methods": ["GET"]},
    "webapps": {
        "url": f"/api/v0/user/{username}/webapps/",
        "allowed_methods": ["GET"],
    },
    "files": {
        "url": f"/api/v0/user/{username}/files/path/var/log/",
        "allowed_methods": ["GET", "DELETE"],
    },
    "websites": {
        "url": f"/api/v1/user/{username}/websites/",
        "allowed_methods": ["GET"],
    },
}

methods = ["GET", "DELETE"]


def get_cpu_quota(username, token):
    response = requests.get(
        f"https://www.pythonanywhere.com/api/v1/user/{username}/websites/",
        headers={"Authorization": f"Token {token}"},
    )
    if response.status_code == 200:
        print("CPU quota info:")
        print(response.json())
    else:
        print(
            f"Got unexpected status code {response.status_code}: {response.content!r}"
        )


def get_op(operation):
    endpoint = endpoints[operation].get("url")
    response = requests.get(
        f"{base_url}{endpoint}",
        headers={"Authorization": f"Token {token}"},
    )
    if response.status_code == 200:
        print(response.json())
    else:
        print(
            f"Got unexpected status code {response.status_code}: {response.content!r}"
        )
    return response.json()


def del_op(operation, file):
    endpoint = endpoints[operation].get("url")
    base = f"{base_url}{endpoint}{file}"
    print(base)
    response = requests.delete(
        base,
        headers={"Authorization": f"Token {token}"},
    )
    # print(response)
    if response.status_code == 204:
        print(f"{file} deleted successfully")
    else:
        print(
            f"Got unexpected status code {response.status_code}: {response.content!r}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch CPU quota from PythonAnywhere API."
    )
    parser.add_argument(
        "--operation", required=False, help="Your PythonAnywhere API token"
    )
    parser.add_argument(
        "--method", required=False, help="Your PythonAnywhere API token"
    )

    args = parser.parse_args()
    # get_cpu_quota(username, token)

    operation = args.operation
    method = args.method
    if operation and method:
        method = method.upper()
        if operation in endpoints.keys():
            if method in endpoints[operation].get("allowed_methods"):
                if method == "GET":
                    get_op(operation)
                if method == "DELETE":
                    files = get_op(operation)
                    if isinstance(files, dict):
                        files = files.keys()
                        for file in files:
                            if not file.endswith("log") or "server" in file:
                                print(file)
                                del_op(operation, file)


import os
import tldextract
import requests
import re
from bs4 import BeautifulSoup
import json

API_KEY = os.environ.get("API_KEY")


def shodan_cli(hostname: str, filename: str):
    try:
        os.mkdir(filename)
        os.chdir(filename)
        run_cmd = f"shodan download --limit 100 {filename}_results hostname:{hostname}"
        os.system(run_cmd)
        parse_cmd = f"shodan parse --fields hostnames --separator , {filename}_results.json.gz > {filename}.json"
        os.system(parse_cmd)
        getting_response(hostname, filename)

    except Exception as e:
        # print(e)
        init_cmd(hostname, filename)


def init_cmd(hostname: str, filename: str):
    shodan_init_cmd = f"shodan init {API_KEY}"
    os.system(shodan_init_cmd)
    shodan_cli(hostname, filename)


def parsing_list_of_domain_names(filename: str):
    with open(f"{filename}.json", 'r') as file:
        # with open("test.json", 'r') as file:
        readed_file = file.read()
        replacing_semicolon = readed_file.replace(";", "\n")
        list_of_domain_names = replacing_semicolon.split("\n")
        print(list_of_domain_names)
    file.close()
    return list_of_domain_names


def getting_response(hostname: str, filename: str):
    list_of_domains = parsing_list_of_domain_names(filename)

    for domain in list_of_domains:
        if "http://" or "https://" not in domain:
            # domain = "https://stg.rds.9c9media.ca"  # + domain
            domain = "https://" + domain
            try:
                response = requests.get(url=domain, timeout=5)
                if response.status_code == 200:
                    print("working:", domain)
                    page_source = response.text
                    save_scraped_results_in_a_file(hostname, page_source)

            except Exception as error:
                print(error)
                pass


def extract_domainName(hostname: str):
    tld = tldextract.extract(hostname)
    domain_name = tld.domain
    return domain_name


def save_scraped_results_in_a_file(hostname: str, page_source):
    with open(hostname, "w") as file:
        file.writelines(page_source)
    file.close()


def ripgrep(folder_name: str):
    with open("regex_keys.json", "r") as json_file:
        json_data = json.loads(json_file.read())

        for item in json_data:
            service_name = item.strip()

            regex = json_data.get(service_name).get("regex")
            grep_cmd = f"rg {regex} {folder_name}"
            os.system(grep_cmd)

    json_file.close()


if __name__ == "__main__":
    # name_of_the_file=extract_domainName("epic.ca")
    # shodan_cli("epic.ca", name_of_the_file)
    # parsing_logic("test")
    # extract_domainName("epic.ca")
    # getting_response("epic.ca")
    ripgrep()

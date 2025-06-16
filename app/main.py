import logging
import requests
import os
from dns import resolver
from . import api
import sys
import time
import re

logging_level = {"INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR" : logging.ERROR, "DEBUG" : logging.DEBUG}

def get_env_opt(key, default):
    """Get optional environment varaiable. If it is not set, the default is returned."""
    val = os.environ.get(key)
    if(val is None):
        return default
    return val

def get_env_req(key, err_message : str):
    """Get required environment variable. If it is no set, an error is logged and the program exits."""
    val = os.environ.get(key)
    if(val is None):
        logging.error(err_message)
        exit(1)
    return val

def get_envs() -> dict:
    env = dict()
    env["username"] = get_env_req("USERNAME", "Please define USERNAME. Exiting...")
    env["domain_number"] = get_env_req("DOMAIN_NUMBER", "Please define DOMAIN_NUMBER. Exiting...")
    env["password"] = get_env_req("PASSWORD", "Please define PASSWORD. Exiting...")
    env["otp_key"] = get_env_opt("OTP_KEY", "")
    env["rrtype"] = get_env_opt("RRTYPE", "A")
    env["domain"] = get_env_req("DOMAIN", "Please define DOMAIN. Exiting...")
    env["subdomain"] = get_env_opt("SUBDOMAIN", "")
    env["interval"] = get_env_opt("INTERVAL", "180")
    env["logging_level"] = get_env_opt("LOGGING", "INFO")
    env["contract"] = get_env_req("CONTRACT", "Please define CONTRACT. Exiting...")
    return env

def validate_env(env: dict):
    """Validates, if the environment variables have valid values."""
    if(env["rrtype"] not in ["A","AAAA"]):
        logging.error("RRTYPE must be either 'A' or 'AAAA'. Exiting...")
        exit(1)
    
    if(not env["interval"].isnumeric()):
        logging.error("INTERVAL must be a number. Exiting..^.")
        exit(1)

    if( env["logging_level"] not in logging_level.keys()):
        logging.error("LOGGING must be one of 'INFO', 'WARNING', 'ERROR' or 'DEBUG'. Exiting...")
        exit(1)




def get_my_public_ip(v6 : bool) -> str:
    """Retrievs own ip address"""
    response = requests.get(f"https://{'v6' if v6 else 'v4'}.ident.me")
    logging.debug(f"My ip address is: '{response.text}'")
    return response.text

def get_remote_ip(domain: str, subdomain: str, rrtype: str) -> str:
    """Retrievs the ip address of the domain"""
    qname = f"{subdomain}.{domain}" if subdomain != "" else domain
    res = resolver.resolve(qname=qname,rdtype=rrtype)
    logging.debug(f"Remote ip address is: '{res[0].to_text()}'")
    return res[0].to_text()


def parse_subdomains(subdomains: str, default_rrtype: str) -> list[tuple[str, str]]:
    """Parse the input string of subdomains. Return tuple of subdomain and rrtype"""
    logging.debug(f"Parsing subdomain string: \"{subdomains}\" with default rrtype: {default_rrtype}...")
    if(not subdomains):
        logging.debug("Subdomains variable empty. Returning default")
        return([("@", default_rrtype)])
    res = []
    for s in subdomains.split(","):
        logging.debug(f"Parsing: \"{s}\"...")
        match = re.match(r"^([^{}]*)(?:\{([^{}]*)\})?$", s)
        if(not match):
            logging.error(f"Invalid value for SUBDOMAIN environment variable: \"{s}\" is not valid.")
            logging.debug(f"Sucessfully parsed: {res}")
            return []
        if not match.group(1):
            logging.warning("Invalid value for SUBDOMAIN environment variable: The comma seperated value must not contain any empty entries or trailing commas. These will be ignored.")
            continue

        res.append((match.group(1), match.group(2) or default_rrtype))
    return res

def check_for_updates(domain: str, subdomain: str, rrtype: str, api : api.Api):
    """Checks, if own ip address differs from the servers. If that is the case, the dns-records are updated."""
    logging.info("Checking for changes...")
    for (sd, rrt) in parse_subdomains(subdomain, rrtype):
        my_ip = get_my_public_ip(rrt == "AAAA")
        remote_ip = get_remote_ip(domain, sd, rrt)
        if(my_ip == remote_ip):
            logging.info(f"DNS records still up to date for: {sd}.{domain} ({rrt}). No update needed.")
            continue
        
        logging.info(f"DNS records are not up to date for: {sd}.{domain} ({rrt}). Updating from '{remote_ip}' to '{my_ip}'.")
        api.renew_session_if_needed()
        if (api.update_address(sd,rrt,my_ip)):
            logging.info("Updating sucessful.")
        

def main():
    """Main funcition."""
    env = get_envs()
    logging.basicConfig(stream=sys.stdout,level=logging_level[env["logging_level"]],format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info("Starting...")
    validate_env(env)
    a = api.Api(username=env["username"],password=env["password"],otp_key=env["otp_key"],domain_number=env["domain_number"],contract=env["contract"])

    interval : int = int(env["interval"])
    while True:
        check_for_updates(env["domain"], env["subdomain"], env["rrtype"], a)
        time.sleep(60 * interval)

if __name__ == "__main__":
    main()

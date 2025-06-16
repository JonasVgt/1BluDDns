import logging
import requests
import os
from dns import resolver
from . import api
import sys
import time

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


env_username = get_env_req("USERNAME", "Please define USERNAME. Exiting...")
env_domain_number = get_env_req("DOMAIN_NUMBER", "Please define DOMAIN_NUMBER. Exiting...")
env_password = get_env_req("PASSWORD", "Please define PASSWORD. Exiting...")
env_otp_key = get_env_opt("OTP_KEY", "")
env_rrtype = get_env_opt("RRTYPE", "A")
env_domain = get_env_req("DOMAIN", "Please define DOMAIN. Exiting...")
env_subdomain = get_env_opt("SUBDOMAIN", "")
env_interval = get_env_opt("INTERVAL", "180")
env_logging_level = get_env_opt("LOGGING", "INFO")
env_contract = get_env_req("CONTRACT", "Please define CONTRACT. Exiting...")

def validate_env():
    """Validates, if the environment variables have valid values."""
    if(env_rrtype not in ["A","AAAA"]):
        logging.error("RRTYPE must be either 'A' or 'AAAA'. Exiting...")
        exit(1)
    
    if(not env_interval.isnumeric()):
        logging.error("INTERVAL must be a number. Exiting..^.")
        exit(1)

    if( env_logging_level not in logging_level.keys()):
        logging.error("LOGGING must be one of 'INFO', 'WARNING', 'ERROR' or 'DEBUG'. Exiting...")
        exit(1)




def get_my_public_ip(v6 : bool) -> str:
    """Retrievs own ip address"""
    response = requests.get(f"https://{'v6' if v6 else 'v4'}.ident.me")
    logging.debug(f"My ip address is: '{response.text}'")
    return response.text

def get_remote_ip(rrtype: str) -> str:
    """Retrievs the ip address of the domain"""
    qname = f"{env_subdomain}.{env_domain}" if env_subdomain != "" else env_domain
    res = resolver.resolve(qname=qname,rdtype=rrtype)
    logging.debug(f"Remote ip address is: '{res[0].to_text()}'")
    return res[0].to_text()


def check_for_updates(api : api.Api):
    """Checks, if own ip address differs from the servers. If that is the case, the dns-records are updated."""
    logging.info("Checking for changes...")
    my_ip = get_my_public_ip(env_rrtype == "AAAA")
    remote_ip = get_remote_ip(env_rrtype)
    if(my_ip == remote_ip):
        logging.info("DNS records still up to date. No update needed.")
        return
    logging.info(f"DNS records are not up to date. Updating from '{remote_ip}' to '{my_ip}'.")
    api.renew_session_if_needed()
    if (api.update_address(env_subdomain,env_rrtype,my_ip)):
        logging.info("Updating sucessful.")
        

def main():
    """Main funcition."""
    logging.basicConfig(stream=sys.stdout,level=logging_level[env_logging_level],format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info("Starting...")
    validate_env()
    a = api.Api(username=env_username,password=env_password,otp_key=env_otp_key,domain_number=env_domain_number,contract=env_contract)

    interval : int = int(env_interval)
    while True:
        check_for_updates(a)
        time.sleep(60 * interval)

if __name__ == "__main__":
    main()

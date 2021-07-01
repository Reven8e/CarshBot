from secrets import steam_user, steam_pssw, cs_user, cs_pssw # Remove

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from dataclasses import dataclass, field

import time, os, threading, datetime, json


@dataclass
class Data:
    default_cashout: int = 1.5
    default_bet: int = 20
    current_bet: int = field(default_factory=int)
    started_balance: int = field(default_factory=int)
    current_balance: int = field(default_factory=int)
    steam_user: str = steam_user # Set login info
    steam_pssw: str = steam_pssw
    cs_user: str = cs_user
    cs_pssw: str = cs_pssw

main = Data()

driver = webdriver.Chrome(ChromeDriverManager().install())


def SteamLogin(steam=True):
    if steam is True:
        driver.find_element_by_xpath('/html/body/div[9]/div[2]/form/a').click()
        driver.find_element_by_xpath('//*[@id="steamAccountName"]').send_keys(Data.steam_user)
        driver.find_element_by_xpath('//*[@id="steamPassword"]').send_keys(Data.steam_pssw)
        driver.find_element_by_xpath('//*[@id="imageLogin"]').click()

    elif steam is False:
        driver.find_element_by_xpath('//*[@id="login_username"]').send_keys(Data.cs_user)
        driver.find_element_by_xpath('//*[@id="login_password"]').send_keys(Data.cs_pssw)
        driver.find_element_by_xpath('/html/body/div[9]/div[2]/form/div[4]/button[1]').click()

    time.sleep(20)


def reload():
    t = threading.Thread(target=time.sleep, args=(1500,))
    t.start()

    return t


def write_json(balance): # Saving data into Logger.json
    main.current_balance = balance
    logger = open("Logger.json", "r+")
    obj = json.load(logger)

    obj.update({str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")): {"Balance": main.current_balance, "Bet": main.current_bet}})
    logger.seek(0), json.dump(obj, logger)

    logger.close()


class Bet:
    @staticmethod
    def signin():
        driver.get('https://csgopolygon.com/')
        SteamLogin(steam=True) # Set False for regular login instead of steam login
        time.sleep(20) # Enter 2FA code for steam and captcha on regular login


    @staticmethod
    def calculate_bet():
        setBet = lambda x: driver.find_element_by_xpath('//*[@id="crash_amount"]').send_keys(x)
        timer = reload()

        while True:
            try:
                balance = int(driver.find_element_by_xpath('//*[@id="balance_p"]').text)

                button = driver.find_element_by_xpath('//*[@id="select_crash"]/div[1]/div[2]/div/div[4]')
                if str(button.text) == "PLACE BET":

                    if balance < main.current_balance:
                        main.current_bet = int(round(main.current_bet*2))
                        driver.find_element_by_xpath('//*[@id="crash_amount"]').clear()
                        setBet(main.current_bet)
                        write_json(balance)

                    elif balance > main.current_balance:
                        main.current_bet = main.default_bet
                        driver.find_element_by_xpath('//*[@id="crash_amount"]').clear()
                        setBet(main.current_bet)
                        write_json(balance)

                    button.click()

                else:
                    time.sleep(3)

            except ValueError:
                pass

            except Exception as e:
                print(e)
                if timer.is_alive() is False:
                    driver.refresh()
                    return

                time.sleep(3)


    @staticmethod
    def StartBet():
        driver.find_element_by_xpath('/html/body/div[27]/div[1]/div[2]/ul/li[5]').click()
        bet_input = driver.find_element_by_xpath('//*[@id="crash_amount"]')
        cashout = driver.find_element_by_xpath('//*[@id="crash_auto_cashout"]')

        bet_input.clear()
        cashout.clear()
        bet_input.send_keys(main.default_bet)
        cashout.send_keys(str(main.default_cashout))
        main.current_balance = int(driver.find_element_by_xpath('//*[@id="balance_p"]').text)
        main.started_balance = int(driver.find_element_by_xpath('//*[@id="balance_p"]').text)
        main.current_bet = main.default_bet


if __name__ == "__main__":
    Bet.signin()
    while True:
        Bet.StartBet()
        Bet.calculate_bet()

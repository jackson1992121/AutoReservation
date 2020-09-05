from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from random import uniform, randrange

def move_to_element(driver, element):
    hov = ActionChains(driver).move_to_element(element)
    hov.perform()

def wait_tag(driver, wait_time, by_string, limit_count = 1, clickable = False, by_type = "css"):
    times = 0
    while True:
        if times < limit_count:
            times = times + 1
        else:
            return None
        try:
            print("waiting tag : {0}...".format(by_string))         
            if clickable:
                if by_type == "css":
                    return_tag = WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.CSS_SELECTOR, by_string)))
                else:
                    return_tag = WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.XPATH, by_string)))
            else:
                if by_type == "css":
                    return_tag = WebDriverWait(driver, wait_time).until(EC.visibility_of_element_located((By.CSS_SELECTOR, by_string)))
                else:
                    return_tag = WebDriverWait(driver, wait_time).until(EC.visibility_of_element_located((By.XPATH, by_string)))
            print("found the tag...")
            return return_tag
        except TimeoutException:
            continue
        except:
            continue

def find_tag(driver, tag_str, wait_time = 0.5, limit_count = 1):
    limit_counts = 0
    while True:
        if limit_counts < limit_count:
            limit_counts = limit_counts + 1
        else:
            print("Could not find the tag")
            return None
        if wait_time > 0.2:
            wait_between(wait_time - 0.2, wait_time + 0.2)
        print("waiting tag {0}...".format(tag_str))
        try:
            cur_tag = driver.find_element_by_css_selector(tag_str)        
            return cur_tag
        except:
            continue

def scroll_down_to(driver, element):
    driver.execute_script("arguments[0].scrollIntoView", element)
    wait_between(0.8, 1)

def wait_between(a, b):
    rand = uniform(a, b)
    sleep(rand)

def select_some_option(driver, select_str, option_str):
    
    select_item = find_tag(driver, select_str, 0.6)
    select_item.click()
    print("select box {0} clicked".format(select_str))

    wait_between(0.5, 0.7)
    option_item = select_item.find_element_by_css_selector(option_str)
    option_item.click()
    print("option {0} clicked".format(option_str))

def login(driver, id, password):
    dialog_input_id = WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "#contener form:nth-of-type(2) input[name='id']")))
    dialog_input_id.send_keys("calcio")

    wait_between(1, 2)

    dialog_input_pw = driver.find_element_by_css_selector( "#contener form:nth-of-type(2) input[name='pw']" )
    dialog_input_pw.send_keys("adam")

    dialog_input_btn = driver.find_element_by_css_selector( "#contener form:nth-of-type(2) input[name='lipw']" )
    dialog_input_btn.click()

    wait_between(1, 2)

def do_search(driver, lesson_no, weekday, hour_range):
    select_some_option(driver, "select[name='mise_cd']", "option[value='{0}']".format(lesson_no))
    wait_between(0.5, 1)
    select_some_option(driver, "select[name='s_hour']", "option[value='{0}']".format(hour_range))
    wait_between(0.5, 1)
    for weekday_item in ["1", "2", "3", "4", "5", "6", "7"]:
        check_box = driver.find_element_by_css_selector("input[value='{0}']".format(weekday_item))
        if check_box != None and check_box.is_selected():
            check_box.click()
            wait_between(0.1, 0.2)
    wait_between(0.5, 1)
    check_box = driver.find_element_by_css_selector("input[value='{0}']".format(weekday))
    if check_box != None and not check_box.is_selected():
        check_box.click()
    wait_between(0.5, 1)
    driver.find_element_by_css_selector("input[type='submit']").click()

def click_confirm():
    btn_rsv = driver.find_element_by_css_selector("input[name='btn_rsv']")

def execute_auto(id, pwd, lesson_id, week_day, time_range):

    # settings for chrome
    chrome_options = Options()
    # Private browsing
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("start-maximized")
    # chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = wd.Chrome(executable_path='chromedriver.exe', options=chrome_options)

    driver.set_page_load_timeout(60)
    driver.get("https://www.goldsgym-membership.jp/reservation")


    # login
    login(driver, id, pwd)

    driver.get("https://www.goldsgym-membership.jp/reservation/reserve/search")

    # execute search
    do_search(driver, lesson_id, week_day, time_range)

    # execute click reserve
    while True:
        p_none = driver.find_element_by_css_selector("p.mgb15")
        if p_none == None or "見つかりました" in p_none.get_attribute('innerHTML'):
            reserve_btn = driver.find_element_by_css_selector("input[name='btn_res']")
            if reserve_btn and reserve_btn.is_enabled():
                break
        btn_back = driver.find_element_by_css_selector("input.btnback")
        btn_back.click()
        btn_search = wait_tag(driver, 10, "input[type='submit']")
        btn_search.click()
        
    reserve_btn.click()

    # input password and click reservation
    input_tag = wait_tag(driver, 10, "input[name='pw']")
    input_tag.send_keys(pwd)

    btn_rsv = driver.find_element_by_css_selector("input[name='btn_rsv']")
    if btn_rsv:
        scroll_down_to(driver, btn_rsv)
    else:
        return False

    # click btn
    btn_rsv.click()

    # check if button clicked
    success = wait_tag(driver, 10, "p.compBox")
    if success == None:
        return False
    else:
        if "予約を完了しました" in success.get_attribute('innerHTML'):
            driver.close()
            driver.quit()
            return True
        else:
            return False

def main():
    result = execute_auto("calcio", "adam", "000001", "2", "00-08")
    wait_between(1000, 10000)
if __name__ == '__main__':
    main()
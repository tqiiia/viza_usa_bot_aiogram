import datetime
import os
import time
import locale
import random
from dateutil.rrule import rrule, MONTHLY
from selenium.webdriver import Keys
from seleniumwire import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from twocaptcha import solver
from auth_data import CAPTCHA_API, login, password

# proxies = [ #
#     '46.232.4.144:8000',
#     '46.3.178.242:8000',
#     '195.208.170.34:8000',
#     '194.5.94.210:8000',
#     '45.91.66.54:8000'
# ]
#
# proxy_options = {
#     "proxy": {
#         "https": f"http://{login}:{password}@{random.choice(proxies)}"
#     }
# }


async def third_cabinet_parser(
        country, first_name, second_name,
        passport_num, board_num, phone,
        email, first_date, second_date
):
    # options = webdriver.ChromeOptions()
    # options.add_argument("start-maximized")
    # options.add_argument('--headless')
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option('useAutomationExtension', False)
    # driver = webdriver.Chrome(options=options,
    #                           seleniumwire_options=proxy_options,
    #                           executable_path=r"C:\py.projects\viza_usa_bot_aiogram\chromedriver.exe")

    # stealth(driver,
    #         languages=["en-US", "en"],
    #         vendor="Google Inc.",
    #         platform="Win32",
    #         webgl_vendor="Intel Inc.",
    #         renderer="Intel Iris OpenGL Engine",
    #         fix_hairline=True,
    #         )

    options = webdriver.FirefoxOptions()
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    options.set_preference("http.response.timeout", 1)
    options.set_preference("dom.max_script_run_time", 1)
    # options.headless = True
    driver = webdriver.Firefox(
        executable_path=r'C:\py.projects\test\geckodriver.exe',
        # seleniumwire_options=proxy_options,
        options=options
    )

    try:
        locale.setlocale(locale.LC_ALL, 'en')
        return_data = []
        driver.get('https://evisaforms.state.gov/Instructions/SchedulingSystem.asp')
        driver.refresh()
        driver.implicitly_wait(20)

        # 1 page

        select_country = Select(driver.find_element(by='name', value='CountryCodeShow'))
        select_country.select_by_visible_text(str(country.split(',')[0]))  # input country

        driver.implicitly_wait(1)

        select_city = Select(driver.find_element(by='name', value='PostCodeShow'))
        select_city.select_by_visible_text(str(country.split(', ', maxsplit=1)[1]))  # input city

        driver.implicitly_wait(1)

        submit = driver.find_element(by='name', value='Submit')
        submit.click()

        driver.implicitly_wait(5)

        # 2 page - captcha

        try:
            captcha = driver.find_element(by='id', value='frmconinput_CaptchaImage')
            captcha.screenshot('captcha.png')

            api_key = os.getenv('APIKEY_2CAPTCHA', CAPTCHA_API)
            solver_captcha = solver.TwoCaptcha(api_key)

            result = solver_captcha.normal('captcha.png')

            time.sleep(2)

            captcha_input = driver.find_element(by='name', value='CaptchaCode')
            captcha_input.send_keys(result['code'].upper())

            driver.implicitly_wait(1)

            submit = driver.find_element(by='name', value='Submit')
            submit.click()

            driver.implicitly_wait(5)

            board_code_input = driver.find_element(by='name', value='nbarcode')

        except Exception as ex:
            print(ex)

            back = driver.find_element(By.XPATH, "//input[@type='button']")
            back.click()

            driver.implicitly_wait(5)

            captcha = driver.find_element(by='id', value='frmconinput_CaptchaImage')
            captcha.screenshot('captcha.png')

            api_key = os.getenv('APIKEY_2CAPTCHA', CAPTCHA_API)
            solver_captcha = solver.TwoCaptcha(api_key)

            result = solver_captcha.normal('captcha.png')

            time.sleep(2)

            captcha_input = driver.find_element(by='name', value='CaptchaCode')
            captcha_input.clear()
            captcha_input.send_keys(result['code'].upper())

            driver.implicitly_wait(1)

            submit = driver.find_element(by='name', value='Submit')
            submit.click()

            driver.implicitly_wait(5)

            board_code_input = driver.find_element(by='name', value='nbarcode')

        finally:
            os.remove('captcha.png')

        # 3 page

        board_code_input.send_keys(str(board_num))

        driver.implicitly_wait(1)

        submit = driver.find_element(by='id', value='link4')
        submit.click()

        driver.implicitly_wait(5)

        # 4 page - calendar

        try:
            first_date = datetime.datetime.strptime(first_date, "%d.%m.%Y")
            second_date = datetime.datetime.strptime(second_date, "%d.%m.%Y")
        except:
            pass

        if first_date == second_date:
            start_month = first_date
        else:
            start_month = '01' + first_date.strftime('.%m.%Y')
            start_month = datetime.datetime.strptime(start_month, "%d.%m.%Y")

        driver.implicitly_wait(5)

        fl = True
        while fl:
            print('Новая итерация')
            driver.implicitly_wait(3)
            for m in rrule(MONTHLY, dtstart=start_month, until=second_date):
                try:
                    # print('Обновили месяц')
                    month = Select(driver.find_element(by='name', value='nDate'))
                    month.select_by_visible_text(f'{str(m.strftime("%B"))} ' + f' {str(m.strftime("%Y"))}')

                    driver.implicitly_wait(2)

                    days = driver.find_elements(By.XPATH, "//td[@valign='top']")
                    for day in days:
                        if m.strftime('%m') == first_date.strftime('%m') \
                                and m.strftime('%m') == second_date.strftime('%m'):
                            # print(int(day.text.split('\n')[0]), int(first_date.strftime('%d')))
                            # print(int(day.text.split('\n')[0]), int(second_date.strftime('%d')))
                            if int(day.text.split('\n')[0]) == int(first_date.strftime('%d')) \
                                    and int(day.text.split('\n')[0]) == int(second_date.strftime('%d')):
                                # print('Проверку прошли')
                                if day.text.split('\n')[1].startswith('Available'):
                                    return_data = str(
                                        day.text.split('\n')[0] + '.' + m.strftime('%m') + '.' + m.strftime('%Y'))
                                    print(return_data)
                                    day.click()
                                    fl = False
                                    break
                                else:
                                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + 'r')
                                    time.sleep(3)
                                    break
                            else:
                                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + 'r')
                                time.sleep(3)
                                break

                        elif m.strftime('%m') == first_date.strftime('%m') \
                                and int(day.text.split('\n')[0]) >= int(first_date.strftime('%d')):
                            if day.text.split('\n')[1].startswith('Available'):
                                return_data = str(
                                    day.text.split('\n')[0] + '.' + m.strftime('%m') + '.' + m.strftime('%Y'))
                                print(return_data)
                                day.click()
                                fl = False
                                break

                        elif m.strftime('%m') == second_date.strftime('%m') \
                                and int(day.text.split('\n')[0]) <= int(second_date.strftime('%d')):
                            if day.text.split('\n')[1].startswith('Available'):
                                return_data = str(
                                    day.text.split('\n')[0] + '.' + m.strftime('%m') + '.' + m.strftime('%Y'))
                                print(return_data)
                                day.click()
                                fl = False
                                break

                        elif m.strftime('%m') != first_date.strftime('%m') \
                                and m.strftime('%m') != second_date.strftime('%m'):
                            if day.text.split('\n')[1].startswith('Available'):
                                return_data = str(
                                    day.text.split('\n')[0] + '.' + m.strftime('%m') + '.' + m.strftime('%Y'))
                                print(return_data)
                                day.click()
                                fl = False
                                break

                except Exception:
                    if len(return_data) == 0:
                        print('Ушли в ошибку')
                        driver.close()
                        driver.quit()
                        await third_cabinet_parser(country, first_name, second_name,
                                                   passport_num, board_num, phone,
                                                   email, first_date, second_date)
        driver.implicitly_wait(5)

        # 5 page

        times = driver.find_elements(By.CLASS_NAME, 'formfield')
        for time_ex in times:
            if str(time_ex).find('AM'):
                time_ex.click()
                time_ex = str(time_ex.get_dom_attribute('value'))
                return_data += str(' ' + time_ex.split()[1] + ' ' + time_ex.split()[2])
                break

        driver.implicitly_wait(1)

        surname_input = driver.find_element(by='id', value='link8b')
        surname_input.send_keys(str(second_name))  # input second_name

        driver.implicitly_wait(1)

        name_input = driver.find_element(by='id', value='link9b')
        name_input.send_keys(str(first_name))

        driver.implicitly_wait(1)

        passport_input = driver.find_element(by='id', value='link10b')
        passport_input.send_keys(str(passport_num))

        driver.implicitly_wait(1)

        email_input = driver.find_element(by='id', value='link11b')
        email_input.send_keys(str(email))

        driver.implicitly_wait(1)

        phone_input = driver.find_element(by='id', value='link12b')
        phone_input.send_keys(str(phone))

        driver.implicitly_wait(1)

        try:
            captcha = driver.find_element(by='id', value='frmconinput_CaptchaImage')
            captcha.screenshot('captcha.png')

            api_key = os.getenv('APIKEY_2CAPTCHA', CAPTCHA_API)
            solver_captcha = solver.TwoCaptcha(api_key)

            result = solver_captcha.normal('captcha.png')

            time.sleep(5)

            captcha_input = driver.find_element(by='name', value='CaptchaCode')
            captcha_input.send_keys(result['code'].upper())
        except Exception as ex:
            print(ex)
            return 'Ошибка в решении капчи. Пожалуйста, введите данные снова'
        finally:
            os.remove('captcha.png')

        accept = driver.find_element(by='id', value='confidentiality')
        accept.click()

        driver.implicitly_wait(1)

        submit = driver.find_element(by='id', value='linkSubmit')
        submit.click()

        time.sleep(10)

        try:
            driver.find_element(By.XPATH, "//font[@color='red']")
            os.remove('End.png')
            return 'Вы ввели неверные данные, попробуйте ещё раз'
        except:
            driver.save_full_page_screenshot('End.png')
            # img = Image.open('End.png')
            # img = img.crop((0, 0, img.size[0] / 2 - 15, img.size[1]))
            # img.save('End.png')
            return f"Записали вас на {return_data.split(' ')[0]} в {return_data.split(' ')[1].split(':')[0]}:{return_data.split(' ')[1].split(':')[1]} {return_data.split(' ')[2]}. Не опаздывайте!"

    except Exception as ex:
        print(ex)
        driver.save_screenshot('Error.png')
        await third_cabinet_parser(country, first_name, second_name, passport_num, board_num, phone, email, first_date, second_date)
        print('ПЕРЕЗАГРУЗКА' * 5)

    finally:
        driver.close()
        driver.quit()

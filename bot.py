from botcity.web import WebBot, Browser, By
from botcity.maestro import *
from botcity.web.util import element_as_select
from botcity.web.parsers import table_to_dict

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False

def main():
    maestro, execution = setup_maestro()
    
    bot = setup_bot()

    # Acessa a página dos Correios e seleciona a UF
    access_correios_website(bot)
    
    # Extrai dados da tabela
    dataTable = extract_table_data(bot)
    
    # Acessa o site do IBGE e pesquisa as cidades
    search_cities_on_ibge(bot, dataTable)

    # Dentro do site do IBGE, pega a poupulação total do município
    getting_population_on_ibge(bot)
    
    finish_task(maestro, execution.task_id)
    

def setup_maestro():
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()
    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")
    return maestro, execution


def setup_bot():
    bot = WebBot()
    bot.headless = False
    bot.browser = Browser.CHROME
    bot.driver_path = r"D:\PythonProjects\chromedriver\chromedriver.exe"
    return bot


def access_correios_website(bot):
    bot.browse("https://buscacepinter.correios.com.br/app/faixa_cep_uf_localidade/index.php")
    bot.maximize_window()
    
    drop_uf = element_as_select(bot.find_element("//select[@id='uf']", By.XPATH))
    drop_uf.select_by_value("SP")
    
    find_btn = bot.find_element("//*[@id='btn_pesquisar']", By.XPATH)
    find_btn.click()
    bot.wait(3000)


def extract_table_data(bot):
    data_table = bot.find_element("//table[@id='resultado-DNEC']", By.XPATH)
    return table_to_dict(table=data_table)


def search_cities_on_ibge(bot, data_table):
    bot.navigate_to("https://cidades.ibge.gov.br/brasil/panorama")
    max_cities = 5
    city_count = 0
    previous_city = ""

    for city in data_table:
        city_name = city["localidade"]
        if city_name == previous_city:
            continue
        
        if city_count < max_cities:
            search_city_on_ibge(bot, city_name)
            city_count += 1
            previous_city = city_name
        else:
            print("Número máximo de cidades alcançado")
            break

    bot.wait(3000)
    bot.stop_browser()


def search_city_on_ibge(bot, city_name):
    search_input = bot.find_element("/html/body/app/shell/header/busca/div/input", By.XPATH)
    search_input.send_keys(city_name)
    
    bot.wait(1000)
    
    search_result = bot.find_element(f"//a[contains(span, '{city_name}')]", By.XPATH)
    search_result.click()
    
    bot.wait(2000)

def getting_population_on_ibge(bot):
    populacao = (bot.find_element("//div(@class='indicador__valor')", By.XPATH)).text


def finish_task(maestro, task_id):
    maestro.finish_task(
        task_id=task_id,
        status=AutomationTaskFinishStatus.SUCCESS,
        message="Task Finished OK."
    )

if __name__ == '__main__':
    main()
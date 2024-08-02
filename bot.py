from botcity.web import WebBot, Browser, By
from botcity.maestro import *
from botcity.web.util import element_as_select
from botcity.web.parsers import table_to_dict

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False

def main():
    # Runner passes the server url, the id of the task being executed,
    # the access token and the parameters that this task receives (when applicable).
    maestro = BotMaestroSDK.from_sys_args()
    ## Fetch the BotExecution with details from the task, including parameters
    execution = maestro.get_execution()

    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    bot = WebBot()

    # Configure whether or not to run on headless mode
    bot.headless = False

    # Uncomment to change the default Browser to Firefox
    bot.browser = Browser.CHROME

    # Uncomment to set the WebDriver path
    bot.driver_path = r"D:\PythonProjects\chromedriver\chromedriver.exe"

    # Opens the BotCity website.
    bot.browse("https://buscacepinter.correios.com.br/app/faixa_cep_uf_localidade/index.php")
    bot.maximize_window()

    # Seleciona uma localidade dentro do seletor de UF
    dropUf = element_as_select(bot.find_element("//select[@id='uf']", By.XPATH))
    dropUf.select_by_value("SP")

    # Clica no botão de pesquisar para procurar localidades
    findBtn = bot.find_element("//*[@id='btn_pesquisar']", By.XPATH)
    findBtn.click

    bot.wait(3000)

    # Tabela de dados baseada na UF
    dataTable = bot.find_element("//table[@id='resultado-DNEC']", By.XPATH)
    dataTableExtract = table_to_dict(table=dataTable)

    bot.navigate_to("https://cidades.ibge.gov.br/brasil/panorama")

    for cidade in dataTable:
        strCidade = cidade["localidade"]

        inputUfIbge = bot.find_element("/html/body/app/shell/header/busca/div/input", By.XPATH)
        inputUfIbge.send_keys(strCidade)

        searchCity = bot.find_element(f"//a[contains(span, '{strCidade}')]", By.XPATH)
        searchCity.click()

    # Wait 3 seconds before closing
    bot.wait(3000)

    # Finish and clean up the Web Browser
    bot.stop_browser()

    # Uncomment to mark this task as finished on BotMaestro
    maestro.finish_task(
        task_id=execution.task_id,
        status=AutomationTaskFinishStatus.SUCCESS,
        message="Task Finished OK."
    )


def not_found(label):
    print(f"Element not found: {label}")


if __name__ == '__main__':
    main()

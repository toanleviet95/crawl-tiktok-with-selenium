from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
import time

# Initialize Chrome WebDriver
driver = webdriver.Chrome(ChromeDriverManager().install())

# XPATH data
XPATH = {
  "avatar": "//div[contains(@class, 'user-page-header') or @data-e2e='user-avatar']/span/img",
  "username": "//h2[contains(@class, 'ShareTitle') or contains(@class, 'share-title')]",
  "following": "//strong[@title='Following']",
  "followers": "//strong[@title='Followers']",
  "likes": "//strong[@title='Likes']",
  "user_bio": "//h2[contains(@class, 'ShareDesc') or contains(@class, 'share-desc')]",
  "is_horizontal_suggested_accounts": "//div[contains(@class, 'suggested-accounts') or contains(@class, 'SuggestedAccounts')]",
  "horizontal_account_item": "//div[contains(@class, 'user-list')]/a",
  "vertical_account_item": "//a[@data-e2e='suggest-user-avatar' or contains(@class, 'user-item')]",
  "see_more": "//p[contains(@class, 'see-more')]",
}

def crawl_user(user_link, XPATH, result, is_crawl_suggested_accounts=False):
  driver.get(user_link)

  # Get avatar
  avatarElement = driver.find_element(By.XPATH, XPATH['avatar'])
  avatar = avatarElement.get_attribute("src")

  # Get username
  usernameElement = driver.find_element(By.XPATH, XPATH['username'])
  username = usernameElement.text

  # Get following
  followingElement = driver.find_element(By.XPATH, XPATH['following'])
  following = followingElement.text

  # Get followers
  followersElement = driver.find_element(By.XPATH, XPATH['followers'])
  followers = followersElement.text

  # Get likes
  likesElement = driver.find_element(By.XPATH, XPATH['likes'])
  likes = likesElement.text

  # Get user bio
  userBioElement = driver.find_element(By.XPATH, XPATH['user_bio'])
  userBio = userBioElement.text

  result.append({
    "avatar": avatar,
    "username": username,
    "following": following,
    "followers": followers,
    "likes": likes,
    "userBio": userBio,
  })

  if is_crawl_suggested_accounts:
    # Get suggested accounts with horizontal UI
    isHorizontal = False
    try:
      isHorizontal = driver.find_element(By.XPATH, XPATH['is_horizontal_suggested_accounts'])
    except:
      isHorizontal = False

    if isHorizontal:
      crawl_with_horizontal_ui(XPATH, result)
    else:
      crawl_with_verrtical_ui(XPATH, result)

def crawl_with_horizontal_ui(XPATH, result):
  try:
    seeMoreElement = driver.find_element(By.XPATH, XPATH['see_more'])
    seeMoreElement.click()
    time.sleep(4)
    horizontalListAccountsElement = driver.find_elements(By.XPATH, XPATH['horizontal_account_item'])
    links = []
    if len(horizontalListAccountsElement) > 0:
      for account in horizontalListAccountsElement:
        href = account.get_attribute("href")
        links.append(href)
      for link in links:
        crawl_user(link, XPATH, result, False)
  except BaseException:
    logging.exception("An exception was thrown !")


def crawl_with_verrtical_ui(XPATH, result):
  try:
    waitElement = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.XPATH, XPATH['vertical_account_item']))
    )
    if waitElement:
      verticalListAccountsElement = driver.find_elements(By.XPATH, XPATH['vertical_account_item'])
      links = []
      if len(verticalListAccountsElement) > 0:
        for account in verticalListAccountsElement:
          href = account.get_attribute("href")
          links.append(href)
      for link in links:
        crawl_user(link, XPATH, result, False)
  except BaseException:
    logging.exception("An exception was thrown !")


def crawl_user_list():
  result = []
  initLink = 'https://www.tiktok.com/@trinhkhanhlinh01'
  crawl_user(initLink, XPATH, result, True)
  driver.quit()
  return {
    "count": len(result),
    "data": result,
  }

print(crawl_user_list())

const puppeteer = require('puppeteer');
const MongoClient = require("mongodb").MongoClient;

const uri = "mongodb://127.0.0.1:27017/";

// define database information
const client = new MongoClient(uri);
const database = client.db("");
const collection = database.collection("");

// returns random integer between min and max
const getRndInteger = (min, max) => {
  return Math.floor(Math.random() * (max - min)) + min;
}

// clicks page button depending on text provided
const clickButton = async (container, text) => {
  const allButtons = await container.$$('[role="button"]');
  for (const btn of allButtons) {
    let value = await btn.evaluate((el) => el.textContent)
    if (value === text) {
      btn.click();
      return true;
    }
  }
  return false;
}

// collects and stores text of first n posts of FB page to database
const getPosts = async (url, name, numberOfPosts) => {
  try {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.setViewport({ width: 1366, height: 768 });
    // load webpage
    await page.goto(url);
    // small wait in order to let it load
    await page.waitForTimeout(2000);

    // clicks cookies button
    await clickButton(page, "Only Allow Essential Cookies");

    await page.waitForTimeout(2000);

    let counter = 1

    while (counter < numberOfPosts) {
      await page.hover('div[aria-posinset="' + counter + '"]');
      const post = await page.$('div[aria-posinset="' + counter + '"]');

      const clickedMoreButton = await clickButton(post, "See more");
      if (clickedMoreButton) await page.waitForTimeout(1000);

      const postText = await post.$eval('div[data-ad-preview="message"]', el => el.textContent);
      try {
        await collection.insertOne({ text: postText, name: name, url: url });
      } catch (error) {
        await client.close();
      }

      await page.waitForTimeout(getRndInteger(2000, 4000));
      counter++;
    }
  } finally {
    await browser.close();
  }
}

// reads fb pages from json file and collects posts from each one
const main = async () => {
  const jsonData = require('./pages.json');
  for (const item of jsonData) {
    if (item.FB_page) {
      try {
        await getPosts(item.FB_page, item.Name_Eng, 10)
        await new Promise(resolve => setTimeout(resolve, 5000));   
      } catch (error) {
        continue;
      }
    }
  }

  await client.close();
}

main();
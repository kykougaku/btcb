function main(value=1) {
  var CCSSid = "1v_YkGEtrbQ7XjAjjCeFPULb2h6Pot3L1Y-u2Dh2vZGw"; 
  var sheet = SpreadsheetApp.openById(CCSSid).getActiveSheet(); 

  var ticker = request("/api/ticker", "btc_jpy", "https://coincheck.com");

  let lastrow=sheet.getDataRange().getLastRow();
  let insrow=lastrow+1

  var formattedDate = Utilities.formatDate(new Date(), "Asia/Tokyo", "yyyy-MM-dd' 'HH:mm:ss+00:00");
  
  
  sheet.getRange(insrow,1).setValue(formattedDate);
  sheet.getRange(insrow,2).setValue(ticker["last"]);
  sheet.getRange(insrow,3).setValue(ticker["bid"]);
  sheet.getRange(insrow,4).setValue(ticker["ask"]);
  sheet.getRange(insrow,5).setValue(ticker["high"]);
  sheet.getRange(insrow,6).setValue(ticker["low"]);
  sheet.getRange(insrow,7).setValue(ticker["volume"]);
  sheet.getRange(insrow,8).setValue(ticker["timestamp"]);
}

function getHTML(URL){
  const response = UrlFetchApp.fetch(URL);
  let result = response;
  if (jsonParse) {
    result = JSON.parse(response.getContentText());
    
  }
  return result;
}
function request(method, pair, url, jsonParse=true) {
  url = url + method;
  const options = {
    pair: pair
  };
  const response = UrlFetchApp.fetch(url, options);
  let result = response;
  if (jsonParse) {
    result = JSON.parse(response.getContentText());
  }
  return result;
}

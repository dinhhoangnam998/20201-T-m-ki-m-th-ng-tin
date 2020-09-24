document.addEventListener('DOMContentLoaded', function() {
    chrome.tabs.executeScript( {
        code: "window.getSelection().toString();"
      }, function(selection) {
        document.getElementById("text-search").value = selection[0];
      });
  }, false);


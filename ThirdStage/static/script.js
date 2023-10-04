
  console.log('This is Javascript')


const numbersToWords = { 0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",8: "eight",
                        9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "Fifteen",
                        16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen", 20: "twenty", 30: "thirty",
                        40: "forty", 50: "fifty", 60: "sixty", 70: "seventy", 80: "eighty", 90: "ninety",
                        };


ONES_ = {0:"", 1:"One", 2:"Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",7: "Seven",8: "Eight", 9: "Nine"}


TEENS_ = {0:"Ten", 1:"Eleven", 2:"Twelve", 3:"Thirteen", 4:"Fourteen", 5:"Fifteen", 6:"Sixteen",
            7:"Seventeen", 8:"Eighteen", 9:"Nineteen"}


TENS_ = {0:"", 1:"", 2:"Twenty", 3:"Thirty", 4:"Forty", 5:"Fifty", 6:"Sixty", 7:"Seventy", 8:"Eighty", 9:"Ninety"}


function convertNumberToWords(number) {

  if (number == 0){
        return 0;
  } else if (number < 0){
        return "minus" + convertNumberToWords(Math.abs(number))
  }else if (number < 10){
        return ONES_[number]
  }else if (number < 20){
        return TEENS_[number - 10]
  }else if (number < 100){
        return TENS_[Math.floor(number / 10)] + " " + convertNumberToWords(number % 10)

  }else if (number < 1000){
        return ONES_[Math.floor(number / 100)] + " Hundred " + " and " + convertNumberToWords(number % 100)
  }else if (number < 1000000){
        return convertNumberToWords(Math.floor(number / 1000)) + " Thousand " + convertNumberToWords(number % 1000)
  }else if (number < 1000000000){
        return convertNumberToWords(Math.floor(number / 1000000)) + " Million " + convertNumberToWords(number % 1000000)
  }else if (number < 1000000000000){
        return convertNumberToWords(Math.floor(number / 1000000000)) + " Billion " + convertNumberToWords(number % 1000000000)
  }else {
        return "Figure very Large"
        }
  };

//        get the values of height for grp tanks
        let h1 = document.getElementById("height_1m").value
        let h2 = document.getElementById("height_2m").value
        let h3 = document.getElementById("height_3m").value
        let h4 = document.getElementById("height_4m").value

        let unitPrice = document.getElementById("unitPrice").value
        let vatPercent = document.getElementById("vat_").value

        let transport = document.getElementById("transportVal").value

        let tankType = document.getElementById("getTankType").innerText;
        let height = document.getElementById("height").innerText;
        let priceOfPanel = document.getElementById("price").innerText;
        let noteOnTransport = ""
        let numberOfPanel = priceOfPanel / unitPrice;
        let unitPriceOfPanel
        let converter

        let amountOfInstallation = document.getElementById("installAmount").innerText;
        let amountOfPanel = document.getElementById("amount").innerText;

//        get installation price
        let installationPriceGrp = document.getElementById("installPriceGrp").value;
        let installationPriceSteel = document.getElementById("installPriceStl").value;

        if (transport == null || transport == 0 ){
            transport = 0
            noteOnTransport = "NOTE: Quote excludes plumbing pipes, stanchion for elevated tank, concrete plinth for ground tank and transportation"
            console.log(transport)
        }else {
            noteOnTransport = "NOTE: Quote excludes plumbing pipes, stanchion for elevated tank and concrete plinth for ground tank"
            console.log(transport)
        }

        if (tankType == "Steel") {
            console.log("I am using Steel ")
            amountOfInstallation = parseInt(installationPriceSteel) * parseInt(numberOfPanel)
            document.getElementById("installPrice").innerHTML = amountOfInstallation
            document.getElementById("installAmount").innerHTML = amountOfInstallation
            let subTotal = amountOfInstallation + parseInt(amountOfPanel) + parseInt(transport);
            document.getElementById("subtotal").innerHTML = subTotal;

            let vat = vatPercent * parseInt(subTotal);
            document.getElementById("vat").innerHTML = vat;

            let total = vat + subTotal;
            document.getElementById("total").innerHTML = total;
            document.getElementById("word").innerHTML = "Total amount in words: " + convertNumberToWords(Math.ceil(total)) + "Naira";
            document.getElementById("note").innerHTML = noteOnTransport;
            document.getElementById("transport").innerHTML = transport;
            console.log(convertNumberToWords(total));

        } else {
               console.log("I am using GRP")
               if (height == 1) {
                    unitPriceOfPanel = numberOfPanel * h1
               } else if (height == 2) {
                    unitPriceOfPanel = numberOfPanel * h2
               } else if (height == 3) {
                    unitPriceOfPanel = numberOfPanel * h3
               } else {
                    unitPriceOfPanel = numberOfPanel * h4
               }
               amountOfInstallation = parseInt(installationPriceGrp) * parseInt(numberOfPanel)
               document.getElementById("installPrice").innerHTML = amountOfInstallation
               document.getElementById("installAmount").innerHTML = amountOfInstallation
               document.getElementById("price").innerHTML = unitPriceOfPanel
               amountPrice = unitPriceOfPanel * 1
               document.getElementById("amount").innerHTML = amountPrice

               let subTotal = amountOfInstallation + parseInt(amountPrice) + parseInt(transport);
               document.getElementById("subtotal").innerHTML = subTotal;

               let vat = vatPercent * parseInt(subTotal);
               document.getElementById("vat").innerHTML = vat;

               let total = vat + subTotal;
               document.getElementById("total").innerHTML = total;
               document.getElementById("word").innerHTML = "Total amount in words: " + convertNumberToWords(Math.ceil(total)) + " Naira";
               document.getElementById("note").innerHTML = noteOnTransport;
               document.getElementById("transport").innerHTML = transport;
        }
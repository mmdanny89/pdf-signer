// Copyright (c) 2022, Danny Molina Morales and contributors
// For license information, please see license.txt


let visted = [];
let current_ = [];


$(document).ready(function(){
		frappe.db.get_single_value('Global Settings PDF Signer', 'always_ask')
		.then(r => {
			if (r === 1) {
				always_ask_when_pdf_uploaded();
			}
		});
});


const OBSERVER = new MutationObserver(function (mutations) {
	for (const mutation of mutations) {
		if (mutation.type === 'attributes') {
			if (mutation.attributeName === 'data-route') {
				current_ = mutation.target.dataset.route.split('/');
				break;
			}		
		  }
	}
	if (current_) {
		if (current_[0] === 'Form') {
			const isFound = visted.some(element => {
				if (String(element) === String(current_[1])) {
					return true;
				}
				return false;
			});
			if(isFound === false) {
				
				frappe.ui.form.on(current_[1], {
					onload: function(frm) {
						frappe.realtime.on("ask_to_sign",function () {
							console.log('dialog here, ready');
						});
					},
				});
				visted.push(String(current_[1]));
			}
		}
	}
});
  

const CONFIG  = {
    childList: true, 
    subtree: true,
	attributes: true
};


function always_ask_when_pdf_uploaded() {
	OBSERVER.observe(document.body, CONFIG);
}


function disble_ask() {
	OBSERVER.disconnect();
}

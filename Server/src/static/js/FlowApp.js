/*
 *
 *
 */

var indicator = null;
var allObj = {};
var currentObj = undefined;
var objInputs = {}; 
var objOutputs = {}; 
var targetImgs = new Array();
var lastCheck = 0;


var pix_per_meter = 6000;

$(document).ready(function() {	
	loadCookieTargets();


	flowConnector = new Flow("DYNAMIC", "108.59.3.115:19708");
	connect();
	
	flowConnector.addEventListener("onclose", function(){
		connect();
	});
	
	lastCheck = new Date().getTime();
    setTimeout(pauseCheck, 1000);
});

function connect(){
	flowConnector.connect(function(){
		flowConnector.sendFlowMsg(flowConnector.serverAddr, "GET_OBJECTS", "200", "", function(msgObj){
			objJson = JSON.parse(msgObj.get_body());
			output = {};
			for (index in objJson){
				flowObj = new FlowObj([objJson[index]]);
				output[flowObj.get_id()] = flowObj.get_imgs();
			}

			if (Utils.getCookie("flow_objects") != JSON.stringify(output)){
				Utils.setCookie("flow_objects", JSON.stringify(output), 365);
				alert("Dam. Late obj bind manual reload needed");
			}
		});
	});	
}
	
window.onbeforeunload = function(e) {
	flowConnector.disconnect();
};

function loadCookieTargets(){
	obj_cookie = Utils.getCookie("flow_objects");
	if (obj_cookie != undefined){
		tmp_objs = JSON.parse(obj_cookie);
		for (index in tmp_objs){
			imgs = tmp_objs[index];
			for (index1 in imgs){		 					
				addTarget(index, imgs[index1]["imgUrl"], imgs[index1]["height"], imgs[index1]["width"]);
			}
			targetImgs.push(index);
		}
	}
}

function addTarget(id, url, height, width){
	var headID = document.getElementsByTagName("head")[0];       
	var cssNode = document.createElement('link');
	cssNode.id = id;
	cssNode.rel = "viper-reference-image";
	cssNode.href = url;
	cssNode.title = "width:"+(width/100)+"m";
	cssNode.title += "; height:"+(height/100)+"m";
	headID.appendChild(cssNode);
		
	var divTag = document.createElement("div"); 
	divTag.id = id+"_node"
	divTag.style.position = "absolute";
	divTag.className = "node"; 
				
	document.getElementById("viper.scene_node").appendChild(divTag);
}
      		
				
function pauseCheck() {
	var now = new Date().getTime();
	var diff = now - lastCheck;
	if (diff > 2000) {
		//alert('took ' + diff + 'ms');
		
		var now = new Date().getTime();
		lastCheck = now;
		setTimeout(pauseCheck, 1000);
	}else{
		lastCheck = now;
		setTimeout(pauseCheck, 1000);
	}
}




//Viper Code

function onViperReady() {
	viper.setLoggingEnabled(false);
	viper.setBrowserBounce(false);
	viper.setTrackingLostAnimationEnabled(false);
	viper.setHtmlResolution(pix_per_meter);
	
	var observer = {
		onMapCreatedWithImage : function(imageId) {
			var elemId = imageId + "_node";
			
			// Show found node, hide the others
			var nodes = document.getElementsByClassName("node");
			for (var i in nodes) {
				var node = nodes[i];
				if (node.id == elemId) {
					onNodeFound(node.id, imageId);
					node.style.display = "block";
				}else {
					node.style.display = "none";
				}
			}
		},
		
		onMapDiscarded : function() {
		},
		
		onTrackingLost : function() {
			onNodeLost();
		},
		
		onTrackingDisabled : function() {
			onNodeLost();
		}
	}
	
	viper.setObserver(observer);
	
	
	$("#odOkBtn").click(function() {
  		$("#objectDetails").fadeOut();
	});

	$("#ui_obj_inputs_btn").addClass("disabled");
	$("#ui_obj_inputs_btn").click(function(event) {
  		event.preventDefault();
  	});
	
	$("#ui_obj_outputs_btn").addClass("disabled");
	$("#ui_obj_outputs_btn").click(function(event) {
  		event.preventDefault();
  	});
  	
  	$("#ui_obj_name_url").addClass("disabled");
	$("#ui_obj_name_url").click(function(event) {
  		event.preventDefault();
  	});
	
	$('.action-select').bind('click', actionSelected);
}

function onAppLoaded() {
	indicator = document.getElementById("indicator");
					
	for (var i in targetImgs) {
		var id = targetImgs[i];
		viper.activateReferenceImage(id);
	}
	
	//viper.requireRealityMap();
}

function onNodeLost() {
	document.getElementById("ui_obj_name").innerHTML = "Searching...";
	$("#ui_obj_inputs_btn").addClass("disabled");
	$("#ui_obj_inputs_btn").click(function(event) {
  		event.preventDefault();
  	});
	
	$("#ui_obj_outputs_btn").addClass("disabled");
	$("#ui_obj_outputs_btn").click(function(event) {
  		event.preventDefault();
  	});
  	
	document.getElementById("ui_obj_inputs_txt").innerHTML = "0 - Inputs";
	document.getElementById("ui_obj_outputs_txt").innerHTML = "0 - Outputs";
	document.getElementById("ui_obj_outputs_list").innerHTML = "";
	document.getElementById("ui_obj_inputs_list").innerHTML = "";
}


Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

function toTitleCase(str){
    return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

function processTest(tmp){
	selectedObject(allObj[tmp]);
}

function selectedObject(obj){
	document.getElementById("ui_obj_name").innerHTML = obj.get_title();
	
	$("#obj_details_title_txt").html(obj.get_title());
	$("#obj_details_body_txt").html(obj.get_details());

	outputs = obj.get_outputs();
	inputs = obj.get_inputs();

	document.getElementById("ui_obj_inputs_txt").innerHTML = ""+Object.size(inputs)+" - Inputs";
	document.getElementById("ui_obj_outputs_txt").innerHTML = ""+Object.size(outputs)+" - Outputs";
	if(Object.size(inputs) > 0){
		$("#ui_obj_inputs_btn").removeClass("disabled");
	}else{
		$("#ui_obj_inputs_btn").addClass("disabled");
	}
	
	if(Object.size(outputs) > 0){
		$("#ui_obj_outputs_btn").removeClass("disabled");
	}else{
		$("#ui_obj_outputs_btn").addClass("disabled");
	}
	
	output = "";
	for (var index in outputs){
		output += '<li><a class="action-select" action="'+index+'" style="height:30px; font-size:20px; padding-top:5px">'+toTitleCase(index)+'</a></li>'
	}			
	document.getElementById("ui_obj_outputs_list").innerHTML = output;
	
	output = "";
	for (var index in inputs){
		output += '<li><a class="action-select" action="'+index+'" style="height:30px; font-size:20px; padding-top:5px">'+toTitleCase(index)+'</a></li>'
	}
	document.getElementById("ui_obj_inputs_list").innerHTML = output;
	
	
	$("#odOkBtn").click(function() {
  		$("#objectDetails").fadeOut();
	});
	
  	$("#ui_obj_name_url").removeClass("disabled");

	output = "";
	for (var index in allObj){
		output += '<li><a class="search-select" action="'+index+'" style="height:30px; font-size:20px; padding-top:5px">'+allObj[index].get_title()+'</a></li>'		
	}
	document.getElementById("ui_obj_name_list").innerHTML = output;
		
	$('.search-select').bind('click', actionSearchSelected);
	$('.action-select').bind('click', actionSelected);
	
	for (var index in outputs){
		if(currentObj != undefined && index in objInputs){
			objOutputs[index] = obj;
			check();
		}
	}
	
	for (var index in inputs){
		if(currentObj != undefined && index in objOutputs){
			objInputs[index] = obj;
			check();
		}
	}
	
	currentObj = obj;
}

function actionSearchSelected(event){
	$("#objectDetails").fadeIn();
	selectedObject(allObj[$(this).attr("action")]);
}

function actionSelected(event){
	list_name = $(this).parent().parent().attr("id");
	if(list_name.indexOf("inputs") != -1){
		objInputs = {}; 
		objInputs[$(this).attr("action")] = currentObj;
	}else{
		objOutputs = {}; 
		objOutputs[$(this).attr("action")] = currentObj;
	}
	
	check();
}

function check(){
	for (var index in objInputs){
		if(index in objOutputs){
			setTransferUI(objInputs[index].get_title(), objOutputs[index].get_title(), toTitleCase(index));
			
			$("#transferContainer").fadeIn();
			$("#tdCancelBtn").click(function() {
  				$("#transferContainer").fadeOut();
			});
			
			$("#tdSendBtn").click(function() {
  				flowConnector.sendFlowMsg(objOutputs[index].get_id(), index, "200", objInputs[index].get_inputs()[index], sucess_failure_lookup);
				objInputs = {}; 
				objOutputs = {};
			});
		}
	}
}

function setTransferUI(input, output, action){
	$("#tdSendBtn").html(action);
	$("#tdOutputTxt").html(output);
	$("#tdInputTxt").html(input);
	$("#tdActionTxt").html(action);
}

function sucess_failure_lookup(msgObj){
	if (msgObj.get_status() != 200){
		alert(msgObj.get_body());
	}else{
		$("#transferContainer").fadeOut();
	}
}

function onNodeFound(nodeId, imageId) {							
				
	if (!(imageId in allObj)){
		flowConnector.getObjDetails(imageId, function(msgObj){
			objJson = JSON.parse(msgObj.get_body());
			flowObj = new FlowObj(objJson);
			allObj[imageId] = flowObj;
							
			processTest(imageId);
		});
	}else{
		processTest(imageId);	
	}					
}
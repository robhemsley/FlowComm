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

var accept_defaults = false;
var highlight = true;


var pix_per_meter = 6000;

$(document).ready(function() {	
	loadCookieTargets();

	//108.59.3.115
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
	count = 0;
	if (obj_cookie != undefined){
		tmp_objs = JSON.parse(obj_cookie);
		for (index in tmp_objs){
			imgs = tmp_objs[index];
			for (index1 in imgs){		 					
				addTarget(count, index, index1, imgs[index1]["imgUrl"], imgs[index1]["height"], imgs[index1]["width"]);
				count += 1;
			}
			targetImgs.push(index);
		}
	}
}

function addTarget(id, objId, imgId, url, height, width){
	var headID = document.getElementsByTagName("head")[0];       
	var cssNode = document.createElement('link');
	cssNode.id = id;
	cssNode.rel = "viper-reference-image";
	cssNode.href = url;
	cssNode.title = "width:"+(width/100)+"m";
	cssNode.title += "; height:"+(height/100)+"m";
	cssNode.setAttribute("objid", objId);
	cssNode.setAttribute("imgid", imgId);
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
	viper.setLoggingEnabled(true);
	viper.setBrowserBounce(false);
	viper.setTrackingLostAnimationEnabled(false);
	viper.setHtmlResolution(pix_per_meter);
	
	var observer = {
		onMapCreatedWithImage : function(imageId) {
			var elemId = imageId + "_node";
			onNodeFound(imageId);

			
			// Show found node, hide the others
			/*var nodes = document.getElementsByClassName("node");
			for (var i in nodes) {
				var node = nodes[i];
				if (node.id == elemId) {
					onNodeFound(node.id, imageId);
					node.style.display = "block";
				}else {
					node.style.display = "none";
				}
			}*/
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
	$("#ui_obj_inputs_list_open").removeClass('open');
	$("#ui_obj_outputs_list_open").removeClass('open');
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

function processTest(objId, imgId){
	selectedObject(allObj[objId], imgId);
}

function selectedObject(obj, imgId){
	if (imgId == undefined){
		imgId = 0;
	}
	document.getElementById("ui_obj_name").innerHTML = obj.get_title();

	imgs = obj.get_imgs();
	viper.log("State:" + imgs[imgId]["state"]);
	viper.log("ID:" + imgId);
	
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
		output += '<li id="'+toTitleCase(index)+'" ><a class="action-select" action="'+index+'" inter-type="output" style="height:30px; font-size:20px; padding-top:5px">'+toTitleCase(index)+'</a></li>'
	}			
	document.getElementById("ui_obj_outputs_list").innerHTML = output;
	
	output = "";
	for (var index in inputs){
		output += '<li id="'+toTitleCase(index)+'" ><a class="action-select" action="'+index+'" inter-type="input" style="height:30px; font-size:20px; padding-top:5px">'+toTitleCase(index)+'</a></li>'
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
	
	found = false;
	for (var index in outputs){
		if(currentObj != undefined && index in objInputs){
			objOutputs = {}; 
			objOutputs[index] = obj;
			check();
			found = true;
		}
	}
	
	for (var index in inputs){
		if(currentObj != undefined && index in objOutputs){
			objInputs = {}; 
			objInputs[index] = obj;
			check();
			found = true;
		}
	}
	
	currentObj = obj;
		
	if(highlight && !found && imgs[imgId]["state"] != null){
		action = $("#"+toTitleCase(imgs[imgId]["state"])).children().attr("action")
		intertype = $("#"+toTitleCase(imgs[imgId]["state"])).children().attr("inter-type")
		
		if ($("#"+toTitleCase(action)).length) {
			$("#"+toTitleCase(imgs[imgId]["state"])).addClass('active');
			$("#"+$("#"+toTitleCase(imgs[imgId]["state"])).parent().attr("id")+"_open").addClass('open');
			
			if (accept_defaults){
				if(intertype == "output"){
					objOutputs = {}; 
					objOutputs[$(this).attr("action")] = currentObj;
				}else{
					objInputs = {}; 
					objInputs[$(this).attr("action")] = currentObj;
				}
				
				setTimeout('check(); $("#ui_obj_inputs_list_open").removeClass("open"); $("#ui_obj_outputs_list_open").removeClass("open");', 1500);
			}
		}
	}else if (accept_defaults && !found && imgs[imgId]["state"] != null){

		action = $("#"+toTitleCase(imgs[imgId]["state"])).children().attr("action")
		intertype = $("#"+toTitleCase(imgs[imgId]["state"])).children().attr("inter-type")

		if ($("#"+toTitleCase(action)).length) {
			if(intertype == "output"){
				objOutputs = {}; 
				objOutputs[$(this).attr("action")] = currentObj;
			}else{
				objInputs = {}; 
				objInputs[$(this).attr("action")] = currentObj;
			}
				
			check();
		}
	}
}

function actionSearchSelected(event){
	$("#objectDetails").fadeIn();
	selectedObject(allObj[$(this).attr("action")]);
}

function actionSelected(event){
	list_name = $(this).parent().parent().attr("id");
	viper.log("LOOK:"+ $(this).attr("action"));
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
	for (var index1 in objOutputs){
		if(index1 in objInputs){
			setTransferUI(objInputs[index1].get_title(), objOutputs[index1].get_title(), toTitleCase(index1));
			
			$("#transferContainer").fadeIn();
			$("#tdCancelBtn").click(function() {
  				$("#transferContainer").fadeOut();
  				objInputs = {}; 
				objOutputs = {};
			});
			
			$('#tdSendBtn').unbind('click');
			$("#tdSendBtn").click({"index": index1}, function(event) {
				obj = objOutputs[event.data.index]
				
  				flowConnector.sendFlowMsg(obj.get_id(), event.data.index, "200", objInputs[event.data.index].get_inputs()[event.data.index], sucess_failure_lookup);
			});
			break;
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
		objInputs = {}; 
		objOutputs = {};
		$("#transferContainer").fadeOut();
	}
}

function onNodeFound(targetId) {							
	objId = $("#"+targetId).attr("objid");
	imgId = $("#"+targetId).attr("imgid");
	
	if (!(objId in allObj)){
		flowConnector.getObjDetails(objId, function(msgObj){
			objJson = JSON.parse(msgObj.get_body());
			flowObj = new FlowObj(objJson);
			allObj[objId] = flowObj;
			processTest(objId, imgId);
		});
	}else{
		processTest(objId, imgId);	
	}					
}
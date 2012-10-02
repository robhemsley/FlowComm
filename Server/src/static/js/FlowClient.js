/*
 *
 *
 */

var indicator = null;
var allObj = {};
var what = {};
var lastObj = undefined;
var targetImgs = new Array();


var pix_per_meter = 6000;

$(document).ready(function() {	
	loadCookieTargets();

	//
	flowConnector = new Flow("DYNAMIC", "108.59.3.115:9000");
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
});
	
window.onbeforeunload = function(e) {
	flowConnector.disconnect();
};

function loadCookieTargets(){
	obj_cookie = Utils.getCookie("flow_objects");
	if (obj_cookie != undefined){
		tmp_objs = JSON.parse(obj_cookie);
		for (index in tmp_objs){
			imgs = tmp_objs[index];
			what[index] = new FlowObj(tmp_objs);
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





//Viper Code

function onViperReady() {
	viper.setLoggingEnabled(true);
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
	indicator.className = "";
}

function processTest(tmp){
	indicator.innerHTML = allObj[tmp].get_details();
	indicator.className = "visible";

	outputs = allObj[tmp].get_outputs();
	inputs = allObj[tmp].get_inputs();
	
	for (var index in outputs){
		if(lastObj != undefined && index in lastObj.get_inputs()){
			flowConnector.sendFlowMsg(tmp, index, "200", lastObj.get_inputs()[index], sucess_failure_lookup);
		}
	}			

	lastObj = allObj[tmp];
}

function sucess_failure_lookup(msgObj){
	if (msgObj.get_status() != 200){
		alert(msgObj.get_body());
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
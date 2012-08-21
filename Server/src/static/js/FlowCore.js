function Flow(deviceAddr, serverURL){
	if (deviceAddr == undefined){
		this.deviceAddr = "DYNAMIC";
	}else{
		this.deviceAddr = deviceAddr;
	}
	
	if (serverURL == undefined){
		this.serverURL = document.domain+"/flowsocket";
	}else{
		this.serverURL = serverURL+"/flowsocket";
	}
					
	this.serverAddr = "000000";
	this.ws = undefined;
	this.registered = 0;
	this.profile = undefined;
	this.handlers = {};
	this.callback = {};
	
	var flow = this;

	var createWs = function(url){
		websocket = 'ws://'+url;
	  
		if (window.WebSocket) {
			ws = new WebSocket(websocket);
		}else if (window.MozWebSocket) {
			ws = MozWebSocket(websocket);
		}else {
			alert('WebSocket Not Supported');
		}
		
		return ws;
	}
	
	var checkConnState = function(){
		if (this.ws == undefined || this.ws.readyState > 1){
			connect();
		}
	}

	this.connect = function(callback){
		this.ws = createWs(this.serverURL);
		this.ws.onmessage = this.onmessage;
		this.ws.onopen = this.onopen;
		this.ws.onclose = this.onclose;
		if (callback != undefined){
			this.callback["000000"] = callback;
		}
	}
	
	this.disconnect = function(){
		this.ws.close(1000, "Client Disconnect");
	}
	
	this.sendFlowMsg = function (toAddr, action, status, body, callback){
		msg = new FlowMsg();
		msg.set_to(String(toAddr));
		msg.set_from(this.deviceAddr);
		msg.set_action(action);
		msg.set_status(status);
		msg.set_body(body)
		if (callback != undefined){
			this.callback[msg.get_id()] = callback;
		}
		this.ws.send(msg.to_string());
	}
	
	this.authenticate = function(){
		this.sendFlowMsg(this.serverAddr, "AUTH_REQUEST", "200");
	}
	
	this.getObjDetails = function(deviceId, callback){
		this.sendFlowMsg(this.serverAddr, "GET_OBJECT", "200", "{\"deviceId\": \""+deviceId+"\"}", callback);
	}
	
	this.processMsg = function(msg){
		msgObj = new FlowMsg(msg);
		
		if (msgObj.get_action() == "AUTH_RESPONSE"){
			if(msgObj.get_status() == 200){
				this.registered = 1
				this.getObjDetails(this.deviceAddr);
			}else{
				this.registered = -1
			}
		}else if(msgObj.get_action() == "AUTH_REQUEST"){
			this.authenticate();
						
		}else if (msgObj.get_action() == "GET_OBJECT_RESPONSE"){
			objJson = JSON.parse(msgObj.get_body());
			flowObj = new FlowObj(objJson);
			if (String(flowObj.get_id()) == String(this.deviceAddr)){
				this.profile = flowObj;
				if (this.callback["000000"] != undefined){
					this.callback["000000"](msgObj);
					delete this.callback["000000"];
				}
			}
		
		}else if(msgObj.get_action() == "SET_ID"){
			this.deviceAddr = JSON.parse(msgObj.get_body())["deviceId"]
			this.authenticate()		          		
		
		}else if(msgObj.get_action() in flow.profile.get_outputs()){
			if (msgObj.get_action() in this.handlers){
				out_msg = msgObj
				if (this.handlers[msgObj.get_action()]["strCast"]){
					out_msg = out_msg.to_string()	
				}
				this.handlers[msgObj.get_action()]["function"](out_msg);
			}
		}	

		if (msgObj.get_id() in this.callback){
			this.callback[msgObj.get_id()](msgObj);
			delete this.callback[msgObj.get_id()];
		}			          	          		
	}
	
	this.addEventListener = function(type, callback) {
		this.callback[type] = callback;
	};

	this.onmessage = function (evt) {
		flow.processMsg(evt.data);
		if ("onmessage" in flow.callback){
			this.callback["onmessage"](evt);
		}
	};
	  
	this.onopen = function() {
		flow.authenticate();
		if ("onopen" in flow.callback){
			flow.callback["onopen"]();
		}
	};
  
	this.onclose = function(evt) {
		if ("onclose" in flow.callback){
			flow.callback["onclose"]();
		}
	};
	
	this.addHandler = function(name, func, strCast){
		if (strCast == undefined){
			strCast = false;
		}
		this.handlers[name] = {"function": func, "strCast": strCast};
		console.log(this.handlers);
	}
}     







function FlowObj(data) {
	this.data = data[0];
	
	this.get_value = function(key){
		if (key in this.data){
			return this.data[key];
		}else{
			return undefined;
		}
	};
	
	this.set_value = function(key, value){
		this.data[key] = value;
	};	
	
	this.get_id = function(){
		return this.get_value("id")
	};
	
	this.get_imgs = function(){
		return this.get_value("targetImgs")
	};
	
	this.get_details = function(){
		return this.get_value("details")
	};
	
	this.get_title = function(){
		return this.get_value("title")
	};
	
	this.get_interfaces = function(){
		return this.get_value("interfaces")
	};
	
	this.get_inputs = function(){
		tmp = this.get_value("interfaces")["input"]
		output = {}
		for (index in tmp){
			output[tmp[index]["action"]] = tmp[index]["body"]
		}
		if (tmp == undefined){
			return {};
		}
		
		return output
	};
	
	this.get_outputs = function(){
		tmp = this.get_value("interfaces")["output"]
		output = {}
		for (index in tmp){
			output[tmp[index]["action"]] = tmp[index]["body"]
		}
		if (tmp == undefined){
			return {};
		}
		return output
	};
}









function FlowMsg(msg) {
	this.msg;

	if (msg == undefined){
		this.msg = {"to": "", "from": "", "action": "", "hash": "", "body": "", "status": "", "timestamp": "", "msgId": Math.floor(Math.random()*999999)};
	}else{
		jsonMsg = {};
		try{
			jsonMsg = JSON.parse(msg);
		}catch(err){}
		
		this.msg = jsonMsg;
	}
	
	this.validate_hash = function(){
		tmp = jQuery.extend(true, {}, this.msg);
		delete tmp["hash"]
		hashOut = $.md5(JSON.stringify(tmp));
		if (this.get_hash() == hashOut){
			return true;
		}else{
			return false;
		}
	};
	
	this.get_value = function(key){
		if (key in this.msg){
			return this.msg[key];
		}else{
			return undefined;
		}
	};
	
	this.set_value = function(key, value){
		this.msg[key] = value;
		if (key != "hash"){
			this.set_hash();
		}
	};	
	
	this.get_to = function(){
		return this.get_value("to")
	};
	
	this.get_from = function(){
		return this.get_value("from")
	};
	
	this.get_action = function(){
		return this.get_value("action")
	};
	
	this.get_body = function(){
		return this.get_value("body")
	};		
	
	this.get_status = function(){
		return this.get_value("status")
	};
	
	this.get_hash = function(){
		return this.get_value("hash")
	};	    
	
	this.get_timestamp = function(){
		return this.get_value("timestamp")
	};	
	
	this.get_id = function(){
		return this.get_value("msgId")
	};	

	this.set_to = function(val){
		this.set_value("to", val);
	};

	this.set_from = function(val){
		this.set_value("from", val);
	};

	this.set_action = function(val){
		this.set_value("action", val);
	};
	
	this.set_body = function(val){
		this.set_value("body", val);
	};			
	
	this.set_status = function(val){
		this.set_value("status", val);
	};
	
	this.set_timestamp = function(val){
		this.set_value("timestamp", val);
	};
	
	this.set_id = function(val){
		return this.set_value("msgId", val)
	};	

	this.set_hash = function(){
		tmp = jQuery.extend(true, {}, this.msg);
		delete tmp["hash"]
		hashOut = $.md5(JSON.stringify(tmp));
		this.set_value("hash", hashOut);
	};

	this.verify = function () {
		return this.foo === this.bar;
	};
	
	this.to_string = function () {
		this.set_timestamp(Math.round(new Date().getTime()/1000.0))
		return JSON.stringify(this.msg)
	};
}
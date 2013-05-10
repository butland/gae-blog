(function() {
    var pluginName = 'localstore';
    var timeOutId = 0;
    var s_key = '_ckeditor_storage_';
	/**
	  whether or not the browser support local storage.
	*/
	function supports_local_storage(){
	    return !!window.localStorage;
	}
  
    if(supports_local_storage()) {
        var startTimer = function(event) {
           /* if(timeOutId) {
                clearTimeout(timeOutId);
            }*/
            var delay = CKEDITOR.config.localstore_delay;
            timeOutId = setTimeout(function () {
                if(event.editor.checkDirty()) {
                    var content = event.editor.getData();
                    window.localStorage.setItem(s_key, content);
                    event.editor.resetDirty();
                }
            }, delay*1000);
        }
        
        CKEDITOR.plugins.add( pluginName, {
        	lang:['zh-cn','en'],
            requires: ['dialog'],
            init : function( editor ) {
            	// start time when key events fire.
                editor.on('key', startTimer);
		        var b = editor.addCommand(pluginName, new CKEDITOR.dialogCommand(pluginName));
				editor.ui.addButton(pluginName, {
				    label: editor.lang.localstore_tip,
				    command: pluginName,
				    icon: this.path + 'images/icon.png'
				});
				CKEDITOR.dialog.add(pluginName, this.path + 'dialogs/dialog.js');
            }
        });
    }
   
})();

/**
* Delay in seconds
*/
CKEDITOR.config.localstore_delay = 3;
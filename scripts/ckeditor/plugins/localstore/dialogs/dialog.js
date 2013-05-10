CKEDITOR.dialog.add('localstore', function(editor) {
	var _escape = function(value){
		return value;
	};
	return {
	 title: editor.lang.localstore_dialog_title,
	 resizable: CKEDITOR.DIALOG_RESIZE_BOTH,
	 minWidth: 510,
	 minHeight: 320,
	 contents: [{
		 id: 'localstore_dialog',
		 name: 'localstore_dialog',
		 label: 'localstore_dialog',
		 title: 'localstore_dialog',
		 elements: [{
			 type: 'textarea',
			 required: true,
			 label: editor.lang.localstore_des,
			 style: 'width:500px;height:300px',
			 rows: 18,
			 id: 'r_content',
			 'default': ''
		 }]
	 }],
	 onLoad: function(){
		/* var r_content = window.localStorage.getItem('_ckeditor_storage_');
		 this.setValueOf('localstore_dialog', 'r_content', r_content);*/
	 },
	 onShow: function(){
		 var r_content = window.localStorage.getItem('_ckeditor_storage_');
		 this.setValueOf('localstore_dialog', 'r_content', r_content);
	 },
	 onOk: function(){
		 var r_content = window.localStorage.getItem('_ckeditor_storage_');
		 editor.insertHtml(r_content);
	 },
	 onCancel: function(){
		 //
	 }
	};
});
/*
Copyright (c) 2003-2010, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

CKEDITOR.editorConfig = function( config )
{
	// Define changes to default configuration here. For example:
	// config.language = 'fr';
	// config.uiColor = '#AADC6E';
	config.toolbar_Basic =
		[
		    ['Source','Preview','localstore'],
		    ['Cut','Copy','Paste','PasteText','PasteFromWord'],
		    ['Undo','Redo','Find','Replace','SelectAll','RemoveFormat'],
		    ['Link','Unlink','Image','Flash','Table','HorizontalRule','Smiley','SpecialChar'],
		    '/',
		    ['Format','Font','FontSize','TextColor','BGColor'],
		    ['Bold','Italic','Underline','Strike','Subscript','Superscript'],
		    ['NumberedList','BulletedList','Outdent','Indent','Blockquote'],
		    ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock']
		];
	config.toolbar = 'Basic';
	config.height = '500px';
	config.filebrowserImageUploadUrl = '/file/upload?type=ckeditor_images';

	config.extraPlugins += ('localstore');
};

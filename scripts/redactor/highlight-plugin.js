if (typeof RedactorPlugins === 'undefined') {
    var RedactorPlugins = {};
}

RedactorPlugins.highlight = {
    init: function () {
        var do_call_back = this.highlightCode;
        this.addBtn('highlight', 'Code HighLight', function(redactor_object, event, button_key) {
            var callback = $.proxy(function(){
                var node = $('<span class="new-element"></span>')[0];
                this.insertNodeAtCaret(node);
//                var current = this.getCurrentNode();
                $("#code_submit").click(function(){
                    do_call_back(redactor_object, node);
                });
            }, redactor_object);

            redactor_object.modalInit('Code HighLight', '<div id="code_highlight">' +
                '<select id="language" name="language">      <option value="awk">Awk</option>      <option value="basemake">Base Makefile</option>      <option value="bash">Bash</option>      <option value="c">C</option>      <option value="csharp">C#</option>      <option value="cpp">C++</option>      <option value="cmake">CMake</option>      <option value="css">CSS</option>      <option value="clojure">Clojure</option>      <option value="coffee-script">CoffeeScript</option>      <option value="common-lisp">Common Lisp</option>      <option value="cython">Cython</option>      <option value="d">D</option>      <option value="dtd">DTD</option>      <option value="dart">Dart</option>      <option value="delphi">Delphi</option>      <option value="diff">Diff</option>      <option value="django">Django/Jinja</option>      <option value="erlang">Erlang</option>      <option value="fortran">Fortran</option>      <option value="go">Go</option>      <option value="groovy">Groovy</option>      <option value="html">HTML</option>    <option value="json">JSON</option>      <option value="java">Java</option>      <option value="jsp">Java Server Page</option>      <option value="js">JavaScript</option>      <option value="lua">Lua</option>      <option value="make">Makefile</option>      <option value="mysql">MySQL</option>      <option value="nginx">Nginx configuration file</option>      <option value="objective-c">Objective-C</option>      <option value="php">PHP</option>      <option value="plpgsql">PL/pgSQL</option>      <option value="perl">Perl</option>      <option value="python">Python</option>      <option value="python3">Python 3</option>      <option value="rb">Ruby</option>   <option value="scala">Scala</option>      <option value="smali">Smali</option>      <option value="velocity">Velocity</option>      <option value="xml">XML</option>      <option value="xslt">XSLT</option>      <option value="yaml">YAML</option>      </select>' +
                '<textarea id="code_content" style="width:580px;height:400px;"></textarea>' +
                '<input type="button" id="code_submit" value="提交" /> ' +
                '</div>', 600, callback);

        });
    },

    highlightCode: function(redactor_object, current) {
        var language = $("#language").val();
        var code = $("#code_content").val();
        $.post("/tools/highlight", { language: language, code: code },
            function (data, status) {
                $(current).replaceWith(data);
                // when click the modal dialog's text area, the origin content-editor lose it's caret, so this does not work
//                redactor_object.insertHtml(data);
                redactor_object.modalClose();

            }
        );
    }
}
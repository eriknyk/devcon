Ext.require([
    'Ext.form.*',
    'Ext.layout.container.Column',
    'Ext.tab.Panel'
]);

Ext.onReady(function(){

    Ext.QuickTips.init();
    Ext.define('Results', {
        extend: 'Ext.data.Model',
        //idProperty: 'name',
        fields: [
            {name: 'user_id', type: 'integer'},
            {name: 'name', type: 'string'},
            {name: 'username', type: 'string'},
            {name: 'problem_title', type: 'string'},
            {name: 'problem_id', type: 'integer'},
            {name: 'result', type: 'string'},
            {name: 'datetime', type: 'string'},
            {name: 'attempt', type: 'integer'}
        ]
    });
    
    var store = Ext.create('Ext.data.Store', {
        model: 'Results',
        autoLoad: true,
        proxy: {
            type: 'ajax',
            url: 'results/getList',
            reader: {
                type: 'json',
                root: 'rows'
            }
        }/*,
        sorters: {property: 'due', direction: 'ASC'},
        groupField: 'project'*/
    });
    
     var grid = Ext.create('Ext.grid.Panel', {
        store: store,
        columns: [
            {
                id       : 'user_id',
                dataIndex: 'user_id',
                hidden: true
            },
            {
                header   : 'User', 
                width    : 80, 
                dataIndex: 'username'
            },
            {
                header   : 'Problem',
                width    : 200,
                dataIndex: 'problem_title'
            },
            {
                header   : 'Result',
                width    : 70,
                dataIndex: 'result'
            },
            {
                header   : 'Date time',
                width    : 120,
                dataIndex: 'datetime'
            },
            {
                header   : 'Attempt',
                width    : 50,
                dataIndex: 'attempt'
            },
            {
                header   : '<>',
                width    : 25,
                renderer : function(v, a, row) {
                  console.log(row.data);
                  return '<a href="#" onclick="showCode('+row.data.user_id+', '+row.data.problem_id+', '+row.data.attempt+')"><img src="/images/Script_go.png"/></a>';
                }
            }
        ],
        stripeRows: true,
//        autoExpandColumn: 'company',
        //height: 350,
        autoHeight: true,
        //width: 600,
        autoWidth: true,
        title: 'Accepted Submits',
        // config options for stateful behavior
        stateful: true,
        stateId: 'grid',
        forceFit: true
    });
    
//    grid.store.load();
    grid.render(document.getElementById('extjs-content'));
});

function showCode(user_id, problem_id, attempt)
{
  Ext.create('Ext.Window', {
        title: 'PHP CODE',
        width: 600,
        height: 500,
        plain: true,
        //headerPosition: 'left',
        closeable: true,
        maximizable: true,
        layout: 'fit',
        items: [
          {
            xtype : "component",
            autoEl : {
                tag : "iframe",
                //src : "results/get_code?user_id="+user_id+"&problem_id="+problem_id+"&attempt="+attempt
                src:"http://192.168.1.42:8080/results/get_code?user_id="+user_id+"&problem_id="+problem_id+"&attempt="+attempt
            }

          }
        ]
    }).show();
}

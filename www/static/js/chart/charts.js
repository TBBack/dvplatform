Array.prototype.max = function(){   
    return Math.max.apply({},this);  
}
Array.prototype.min = function(){   
    return Math.min.apply({},this);
}

var date = 0;
var mapType = "china";

$('document').ready(function(){
    refresh_canvas();
    countryLine();
    $("#back").on("click",function (event){
        event.stopPropagation();
        $("#back").css("display","none");
        mapType="china";
        date--;
        refresh_canvas();
        clearInterval(timer);
        timer = setInterval(refresh_canvas,1500);
    });
    $("body").on("click",function(event){
        $("#select").removeClass("active");
        $("div.combo-box-wrapper").css("display","none");
    });
    $("#select").on("click",function(event){
        event.stopPropagation();
        $("div.combo-box-wrapper").toggle();
        if($("#select").attr("class")=="combo-box"){
            $("#select").addClass("active");
        }else{
            $("#select").removeClass("active");
        }
    });
});

function initBar(id,date,config){
    var chart = {
        get_value: function (){
            if(mapType=="china"){
                var x_data = [];
                var y_data = [];
                for(var i=0;i<prov_data[date].length;i++){
                    x_data.push(prov_data[date][i].name);
                    y_data.push(prov_data[date][i].value);
                }
                return [x_data.slice(0,10),y_data.slice(0,10)];
            }else{
                var prov_city = get_cities();
                var city_list = prov_city[mapType];
                var y_data = [];
                var dicts = {};
                for(var j=0;j<city_data[date].length;j++){
                    dicts[city_data[date][j].name] = city_data[date][j].value;
                }
                for(var i=0;i<city_list.length;i++){
                    y_data.push(dicts[city_list[i]]);
                }
                return [city_list.slice(0,10),y_data.slice(0,10)];
            }
        },
        configOption: function(){
            var option = {};
            if(mapType=="china"){
                var Max = 2000000;
            }else{
                var Max = 500000;
            }
            
            var data = this.get_value();
            var x_data = data[0];
            var y_data = data[1];
            option = {
                xAxis:[
                    {
                        type:'category',
                        axisLabel:{interval:0,formatter:function(v){
                            var count = 0;
                            var str = "";
                            for(var i=0;i<v.length;i++){
                                str += v[i];
                                count += 1;
                                if(count==3){
                                    count = 0;
                                    str += "\n";
                                }
                            }
                            return str;
                        }},
                        data:x_data,
                        splitLine:{show:false}
                    }
                ],
                yAxis:[{type:'value',max:Max}],
                series:[{'data':y_data,name:config.name,type:'bar'}]
            };
            option.title = config.title;
            option.tooltip = {show:true};
            option.grid = {y:40};
            return option;
        },
        init: function (){
            var myChart = echarts.init(document.getElementById(id));
            var option = this.configOption();
            myChart.setOption(option);
            window.onresize = myChart.resize;
        }
    };
    chart.init();
}

function countryBar(date){
    initBar("bar",date,
        {
            title:{text:"搜索量排名top10",x:"center",y:"top"},
            name:"搜索量",
        }
    );
}

function refresh_canvas(){
    $(".icon-iconfontlingxing1").attr("class","iconfont icon-iconfontlingxing");
    $('#'+date).attr('class','iconfont icon-iconfontlingxing1');
    countryMap(date);
    countryBar(date);
    countryLine(date);
    if($('#play-button').attr('class')=='iconfont1 icon-play'){
        if(date<14){
            date++;
        }else{
            date = 0;
        }
    }
}

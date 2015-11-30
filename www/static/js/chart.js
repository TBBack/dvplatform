var ECHARTS_PATH = "http://echarts.baidu.com/build/dist"

/*图表配置构造函数*/
function initOption(DOMid, title, subtitle, legend, x_axis, y_axis, y_unit) {
    this.DOMid = DOMid;//DOMid
    this.title = title;//图表标题
    this.subtitle = subtitle;//图表副标题
    this.legend = legend;//图例名称
    this.x_axis = x_axis;//X轴
    this.y_axis = y_axis;//Y轴
    this.y_unit = y_unit;//Y轴单位
}
function Bar(Option){
    require.config({
        paths: { echarts: ECHARTS_PATH }
    });
    require([ 'echarts', 'echarts/chart/bar' ], 
        function (ec) {
            var myChart = ec.init(document.getElementById(Option.DOMid));
            var option = {
                title : {
                    text: Option.title,
                    subtext: Option.subtitle
                },
                tooltip: {
                    show: true
                },
                legend: {
                    data:Option.legend
                },
                xAxis : [
                {
                    type : 'category',
                    data : Option.x_axis
                }
                ],
                yAxis : [
                {
                    type : 'value',
                    axisLabel : {
                        formatter: '{value}' + Option.y_unit
                    }
                }
                ],
                series : [
                {
                    "name":Option.legend[0],
                    "type":"bar",
                    "data":Option.y_axis
                }
                ]
            };
            myChart.setOption(option); 
        }
    );
}

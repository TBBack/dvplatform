function generate_data(data){
    var result = [];
    var avg = 0;
    for(var i=0;i<data.length;i++){
        avg+=data[i];
    }
    avg /=data.length;
    for(var i=0;i<data.length;i++){
        if(data[i]>avg){
            result.push({
                value : data[i],
                itemStyle:{normal:{color:["red"]},}
            });
        }else{
            result.push({
                value : data[i],
                itemStyle:{normal:{color:["orange"]},}
            });
        }
    }
    return result;
}

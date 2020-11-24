document.addEventListener('DOMContentLoaded', function(){
    document.querySelector("#id_Province").addEventListener('change', (event) => {
        var selectedValue = event.target.value;  
        const searchParams = new URLSearchParams({
            'province': selectedValue,
        });
        var url = '/get/district/?'+searchParams.toString();  
    
        fetch(url)
        .then(function(response) {
            return response.text();
        })
        .then(function(text) {
            var elmDistrict = document.querySelector("#id_District");
            elmDistrict.innerHTML = text;
            elmDistrict.value = null;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
                
    });

    document.querySelector("#id_Incident_Type").addEventListener('change', (event) => {
        var selectedValue = event.target.value;  
        const searchParams = new URLSearchParams({
            'incidenttype': selectedValue,
        });
        var url = '/get/subtype/?'+searchParams.toString();  
    
        fetch(url)
        .then(function(response) {
            return response.text();
        })
        .then(function(text) {
            var elmDistrict = document.querySelector("#id_Incident_Subtype");
            elmDistrict.innerHTML = text;
            elmDistrict.value = null;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
                
    });
})
                                                            $("#province").change(function() {
                                                                $("#citymun").empty();
                                                                $("#barangay").empty();
                                                                document.getElementById("barangay").disabled = true;
                                                                $("#citymun").append('<option selected="true" disabled>Choose City/Municipality</option>');
                                                                $("#barangay").append('<option selected="true" disabled>Choose Barangay</option>');
                                                                $.ajax({
                                                                    type: "POST",
                                                                    url: "/8A1E349E01BF6920F5508F2B89CB6C3E94D8C9975F12A9F9602699108AFD55111BB6372DBFD92FE6244E54B81DA23801B12C4715C713F14FBB014388E84621F1",
                                                                    contentType: 'application/json; charset=utf-8',
                                                                    data: $("#province").val(),
                                                                    success: function(data) {
                                                                    $.each(data.cities, function(i, obj){
                                                                            $('#citymun').append($('<option>').text(obj.citymunDesc).attr('value', obj.citymunCode));
                                                                    });
                                                                        document.getElementById("citymun").disabled = false;
                                                                       

                                                                    }
                                                                });
                                                                
                                                            });
                                                                
                                                                $("#citymun").change(function() {
                                                                $("#barangay").empty();
                                                                $("#barangay").append('<option selected="true" disabled>Choose Barangay</option>');
                                                                $.ajax({
                                                                    type: "POST",
                                                                    url: "/E5F2C1589E6E036E7708D7D8C75BDB9F91B54E97A7C5C50AA4F0E1408A091556D34A0AEE2D3F1FF3596DDD3C2186B09F163753AC1095D8420FD4CB476569AB67",
                                                                    contentType: 'application/json; charset=utf-8',
                                                                    data: $("#citymun").val(),
                                                                    success: function(data) {
                                                                    $.each(data.brgy, function(i, obj){
                                                                            $('#barangay').append($('<option>').text(obj.brgyDesc).attr('value', obj.brgyCode));
                                                                    });
                                                                        document.getElementById("barangay").disabled = false;
                          
                                                                    }
                                                                });
                                                                
                                                            });
                                                                $("#barangay").change(function() {
                                                            });
                                                                
class OkoDriveMap { // Имя класса
    // Конструктор будет получать ряд параметров и присваивать их в качестве свойств создаваемому объекту
    constructor(id, settings) {
        this.id = id
        this.settings = settings

        this.init();
    }

    parkingSessions = [];//здесь лежат отрисованные парковочне сессии
    randomMarkers = [];//здесь лежат случайные точки
    deviceTraceLayer = [];//здесь лежат маркеры маршрута устройства
    layers = [];//здесь лежат отриосванные слои
    drawing = null;//в этом слое рисуем
    tempPoint = null;//временная точка для обозначения положения курсора
    show_parking_sessions = true;//это нужно для предотвращения вывода слишком большого количества парковочных сессий на карту
    // Это будут методы объекта
    //инициализация приложения
    init = function () {

        this.initMap();
    }

    //инициализация карты
    initMap = function () {
        this.map = L.map(this.id).setView({
            lon: this.settings.view.lon,
            lat: this.settings.view.lat
        }, this.settings.view.scale);

        var LeafIcon = L.Icon.extend({
            options: {
                iconSize: [16, 16],
            }
        });

        var parkingGreyIcon = new LeafIcon({
            iconUrl: '/images/parking-icon-grey.png'
        });
        var parkingGreenIcon = new LeafIcon({
            iconUrl: '/images/parking-icon-green4.png'
        });

        // show the scale bar on the lower left corner
        L.control.scale({
            imperial: true,
            metric: true
        }).addTo(this.map);

        // show a marker on the map
        //L.marker({lon: 0, lat: 0}).bindPopup('The center of the world').addTo(map);

        //Добавляем на нашу карту слой OpenStreetMap
        L.tileLayer.provider('CartoDB.VoyagerLabelsUnder').addTo(this.map);

        //Выключаем zoom
        this.map.scrollWheelZoom.disable()

        //Активируем/деактивируем карту по клику
        let self = this;
        this.map.on('click', function (ev) {
            if (self.map.scrollWheelZoom.enabled()) {
                self.map.scrollWheelZoom.disable();
                $('#'+ self.id).css('border', '1px solid var(--body-bg)');
            } else {
                self.map.scrollWheelZoom.enable();
                $('#'+ self.id).css('border', '1px solid var(--header-bg)');
            }
        });

        //двигаем мышь над картой
        this.map.on('mousemove', this.mapMouseMove, this);
    }

    mapMouseMove = function (ev) {
        if (!this.drawing) {
            return;
        }

        if (!this.tempPoint) {
            this.tempPoint = L.marker(ev.latlng).addTo(this.map);
        } else {
            //this.tempPoint
        }
    }

    //загружает данные для слоя
    loadLayer = function (layerName) {
        let self = this;
        $.get(
            route('map.loadLayerData', layerName),
            {},
            function (data, textStatus) {
                self.drawLayer(layerName, data);
            },
            'json'
        );
    }

    //рисует слой
    drawLayer = function (layerName, geoJsonData) {

        if (!geoJsonData || !geoJsonData.features) {
            return;
        }

        this.layers[layerName] = L.geoJSON(geoJsonData, {
            style: this.getLayerGeoJSONStyle(layerName),
        }).bringToFront().addTo(this.map);
    }

    //удаляет слой
    removeLayer = function (layerName) {
        if (this.layers[layerName]) {
            this.map.removeLayer(this.layers[layerName]);
            this.layers[layerName] = null;
        }
    }

    //возврщает данные для указанного слоя в формате geoJSON
    getLayerGeoJSONStyle = function (layerName) {
        switch (layerName) {
            case 'parkings': return {
                color: '#3388ff',
                weight: 1,
            };
            case 'roads':
            case 'roads-0':
            case 'roads-1':
            case 'roads-2':
            case 'roads-3':
            case 'roads-4':
                return {
                    color: '#000',
                    weight: 1,
                };
        }
    }

    //
    startDrawingAnArea = function () {
        this.drawing = {
            'points': [],
            'lines': [],
        };
    }

    //добавляет на карту num случайных точек
    drawRandomPoints = function (num) {
        let
            k = Math.pow(10, 15),
            lat_min = 55.63070944654683 * k,
            lat_max = 55.803982452763975 * k,
            lng_min = 37.47573852539063 * k,
            lng_max = 37.79571533203126 * k,
            lat_random, lng_random;

        for (let i = 0; i < num; i++) {
            lat_random = (Math.random() * (lat_max - lat_min) + lat_min) / k;
            lng_random = (Math.random() * (lng_max - lng_min) + lng_min) / k;

            this.randomMarkers.push(L.marker([lat_random, lng_random], {
                title: "Маркер №" + i,
                alt: "ккой-то текст",
            }).addTo(this.map).on('click', function (ev) {
                var popup = L.popup({ offset: [0, -23] })
                    .setLatLng(ev.sourceTarget._latlng)
                    .setContent('<p>Hello!<br />This is a popup for ' + ev.sourceTarget.options.title + '.</p>')
                    .openOn(this.map);

                this.randomMarkers.push(popup);
            }, this));

        }
    }

    removeRandomPoints = function () {
        for (var i in this.randomMarkers) {
            this.randomMarkers[i].remove();
        }
        this.randomMarkers = [];
    }

    loadDeviceHistory = function (url) {
        this.clearDeviceTrace();

        if (!url) {
            return;
        }

        let self = this;

        $.get(
            url,
            {},
            function (data, textStatus) {
                self.drawDeviceTrace(data);
            },
            'json'
        );
    }

    clearDeviceTrace = function () {
        for (var i in this.deviceTraceLayer) {
            this.deviceTraceLayer[i].remove();
        }
        this.deviceTraceLayer = [];
    }

    drawDeviceTrace = function (device_history_data) {
        let lat, lng,
            latLng,
            southWest = null,
            northEast = null,
            iconGreen = L.icon(this.settings.icons.route_green),
            iconRed = L.icon(this.settings.icons.route_red),
            icon;
        //bounds = L.latLngBounds(southWest, northEast);

        for (let i in device_history_data) {
            lat = device_history_data[i].latitude;
            lng = device_history_data[i].longitude;

            if (!southWest) {
                southWest = L.latLng(lat, lng);
            } else {
                southWest = L.latLng(Math.min(lat, southWest.lat), Math.min(lng, southWest.lng));
            }

            if (!northEast) {
                northEast = L.latLng(lat, lng);
            } else {
                northEast = L.latLng(Math.max(lat, northEast.lat), Math.max(lng, northEast.lng));
            }

            if (device_history_data[i].okodrive_status == "out_car") {
                icon = iconRed;
            } else {
                icon = iconGreen;
            }

            latLng = L.latLng(lat, lng);

            this.deviceTraceLayer.push(
                L.marker(latLng, {
                    title: latLng.lat + ' ' + latLng.lng,
                    icon: icon
                })
                    .on('click', function (ev) {
                        var popup = L.popup({ offset: [0, -1] })
                            .setLatLng(ev.sourceTarget._latlng)
                            .setContent('position: ' + ev.sourceTarget._latlng.lat + ' ' + ev.sourceTarget._latlng.lng + '<br>status: ' + device_history_data[i].okodrive_status)
                            .openOn(this.map);

                        this.deviceTraceLayer.push(popup);
                    }, this)
                    .addTo(this.map)
            );
        }

        this.map.fitBounds(L.latLngBounds(southWest, northEast));
    }


    //ПАРКОВОЧНЫЕ СЕССИИ
    /**
     * получает данные для парковочных сессий с указанным стаутсом status_name
     */
    loadParkingsSessions = function (filter) {
        let self = this;

        this.removeParkingsSessions();

        if (Object.keys(filter).length == 0) {
            return;
        }

        if (Object.keys(filter).length == 1 && (Object.keys(filter)[0] == 'date_start_from' || Object.keys(filter)[0] == 'date_start_to')) {
            return;
        }

        //загружаю только парковки, которые входят в текущую область видимости карты
        let bounds = this.map.getBounds();

        filter.lat_max = bounds._northEast.lat;
        filter.lat_min = bounds._southWest.lat;
        filter.lng_max = bounds._northEast.lng;
        filter.lng_min = bounds._southWest.lng;

        this.showAjaxLoader();

        $.get(
            this.settings.parking_sessions_data_url,
            filter,
            function (data, textStatus) {
                self.hideAjaxLoader();

                if(Object.keys(data).length > self.settings.parking_sessions_max_size && self.show_parking_sessions) {
                    self.show_parking_sessions = confirm("Получено слишком большое количество сессий - "+ Object.keys(data).length +"шт. Рекомендуется увеличить масштаб карты или изменить условия фильтра и выполнить поиск заново.\n'ОК' - все равно вывести сессии.\n'Отмена' - изменить условия поиска.");
                }

                if (Object.keys(data).length == 0 || !self.show_parking_sessions) {
                    return;
                }

                self.drawParkingsSessions(data);
            }
        );
    }

    showAjaxLoader = function() {
        if(this.settings.filter_form_loader_indicator_selector) {
            $(this.settings.filter_form_loader_indicator_selector).stop().fadeIn();
        }
    }
    hideAjaxLoader = function() {
        if(this.settings.filter_form_loader_indicator_selector) {
            $(this.settings.filter_form_loader_indicator_selector).stop().fadeOut();
        }
    }

    //удаляет с карты нарисованные парковочные сессии из json_data
    drawParkingsSessions = function (json_data) {
        let
            self = this,
            latLng,
            southWest,// = bounds.southWest,
            northEast,// = bounds.northEast,
            lat, lng;

        for (let i in json_data) {
            lat = json_data[i].lat;
            lng = json_data[i].lng;

            latLng = L.latLng(lat, lng);

            if (!southWest) {
                southWest = L.latLng(lat, lng);
            } else {
                southWest = L.latLng(Math.min(lat, southWest.lat), Math.min(lng, southWest.lng));
            }

            if (!northEast) {
                northEast = L.latLng(lat, lng);
            } else {
                northEast = L.latLng(Math.max(lat, northEast.lat), Math.max(lng, northEast.lng));
            }

            let popup = L.popup({ offset: [-5, -15] })
                .setLatLng(latLng)
                .setContent(this.getParkingSessionHtml(json_data[i])
                    
                );

            this.parkingSessions.push(popup,
                L.marker(latLng, {
                    title: latLng.lat + ' ' + latLng.lng,
                    icon: L.icon(this.settings.icons.parking_blue)
                }).bindPopup(popup)
                    .on('click', function (ev) {
                        ev.sourceTarget._popup.openOn(self.map);
                    }, this)
                    .addTo(this.map)
            );
        }
    }

    getParkingSessionHtml = function(data) {
        let date_start = new Date(data.date_start).toLocaleString('ru-RU', {dateStyle: 'short', timeStyle: 'short'});
        let date_end = new Date(data.date_end).toLocaleString('ru-RU', {dateStyle: 'short', timeStyle: 'short'});
        
        return "<a href=\"https://yandex.ru/maps?l=sat%2Cskl%2Ccarparks&mode=whatshere&source=wizgeo&utm_medium=maps-desktop&utm_source=serp&whatshere%5Bpoint%5D="+ data.lng +"%2C"+ data.lat +"&whatshere%5Bzoom%5D=19&z=19\" target=\"_blank\">В Яндекс карты</a>\n"
        + '<br>даты: '+ date_start +' - '+ date_end
        + '<br>координаты: ' + data.lat + ' ' + data.lng
        + '<br>статус: ' + data.status
        + '<br>комментарий: ' + data.comment
        + '<br>комментарий водителя: ' + data.driver_comment
        + '<br>driver_disagrees: ' + (data.driver_disagrees ? "Нет" : "Да")
        + '<br><br><a href="#" class="set-parking-type-button" data-type="taxi-parking" data-uuid="'+ data.uuid +'">Это парковка для такси</a>'
        + ' <a href="#" class="set-parking-type-button" data-type="no-parking" data-uuid="'+ data.uuid +'">Тут нет парковки</a>';
    }

    //удаляет с карты нарисованные парковочные сессии с указанным status_id
    removeParkingsSessions = function () {
        for (let i in this.parkingSessions) {
            this.parkingSessions[i].remove();
        }
        this.parkingSessions = [];
    }
}
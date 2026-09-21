ROUTES = [
    {
        'id': 'metro-01',
        'transport_type': 'metro',
        'name': 'الخط الأول - حلوان / المرج',
        'total_stops': 35,
        'base_price': 8,
        'is_active': True,
        'stops': ['حلوان', 'عين حلوان', 'مارجرجس', 'السيدة زينب', 'الشهداء', 'المرج'],
    },
    {
        'id': 'train-01',
        'transport_type': 'train',
        'name': 'السكة الحديد - القاهرة / الإسكندرية',
        'total_stops': 12,
        'base_price': 25,
        'is_active': True,
        'stops': ['رمسيس', 'بنها', 'طنطا', 'دمنهور', 'الإسكندرية'],
    },
    {
        'id': 'microbus-01',
        'transport_type': 'microbus',
        'name': 'الميكروباصات داخل القاهرة الكبرى',
        'total_stops': 18,
        'base_price': 6,
        'is_active': True,
        'stops': ['العباسية', 'رمسيس', 'التحرير', 'الجيزة', '6 أكتوبر'],
    },
]


def search_routes(query: str | None = None, transport_type: str | None = None) -> dict:
    items = ROUTES
    if query:
        lowered = query.lower()
        items = [route for route in items if lowered in route['name'].lower() or any(lowered in stop.lower() for stop in route['stops'])]
    if transport_type:
        items = [route for route in items if route['transport_type'] == transport_type]
    return {'items': items}


def get_route_stops(route_id: str) -> dict:
    route = next((item for item in ROUTES if item['id'] == route_id), None)
    if route is None:
        return {'route_id': route_id, 'stops': []}
    return {
        'route_id': route_id,
        'stops': [
            {'name': stop, 'stop_order': index + 1}
            for index, stop in enumerate(route['stops'])
        ],
    }


def realtime_routes() -> dict:
    return {
        'items': [
            {'route_id': route['id'], 'status': 'normal', 'delay_minutes': 3 if route['transport_type'] == 'metro' else 8}
            for route in ROUTES
        ]
    }

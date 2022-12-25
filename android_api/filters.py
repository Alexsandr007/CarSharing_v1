from .models import Device
from rangefilter.filter import DateRangeFilter
from django.contrib import admin
import datetime
from django.db.models import *
from django.db.models.fields import FloatField, IntegerField


class OrderPlacedFilter(DateRangeFilter):
    """
    This filter is being used in django admin panel in profile model.
    It filters out the customers who have placed orders in specified time limit.
    """
    parameter_name = 'placed_at'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_gte = '{}__gte'.format(self.parameter_name)
        self.lookup_kwarg_lte = '{}__lte'.format(self.parameter_name)
        field = Device._meta.get_field('created_at')
        super(DateRangeFilter, self).__init__(field, request, params, Device, admin.site._registry[Device],
                                              "created_at")
        self.request = request
        self.form = self.get_form(request)

    def queryset(self, request, queryset):
        if not self.used_parameters:
            return queryset
        if self.form.is_valid():
            validated_data = dict(self.form.cleaned_data.items())
            if validated_data and (validated_data['created_at'] or validated_data['created_at']):
                order_placed_user = [order['created_at'] for order in Device.objects.filter(
                    **self._make_query_filter(request, validated_data)).distinct('created_at').values("created_at")]
                return queryset.filter(id__in=order_placed_user)
        return queryset

    def _make_query_filter(self, request, validated_data):
        """
        This method overrides the default kwargs generator for date_filter
        :param request:
        :param validated_data:
        :return:
        """
        query_params = {}
        date_value_gte = validated_data.get(self.lookup_kwarg_gte, None)
        date_value_lte = validated_data.get(self.lookup_kwarg_lte, None)

        if date_value_gte:
            query_params['{0}__gte'.format(self.field_path)] = self.make_dt_aware(
                datetime.datetime.combine(date_value_gte, datetime.time.min),
                self.get_timezone(request),
            )
        if date_value_lte:
            query_params['{0}__lte'.format(self.field_path)] = self.make_dt_aware(
                datetime.datetime.combine(date_value_lte, datetime.time.max),
                self.get_timezone(request),
            )

        return query_params

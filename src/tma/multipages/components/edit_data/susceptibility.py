import solara
from solara import Reactive

from tma.core.data.parser.model.parameter import Parameter
from tma.core.service.sample.controller.sample_controller import SampleController
from tma.core.service.sample.model.specimen_item import SpecimenItem

"""
This module provides a component for handling exclusive checkboxes related to specimen parameters.

Attributes:
    active_checkbox (solara.Reactive): Reactive object representing the active checkbox.
    available_checkboxes (solara.Reactive): Reactive object representing the availability of checkboxes.

"""


@solara.component
def ExclusiveCheckboxes(sample_controller: SampleController, file_reference: Reactive[SpecimenItem]):
    """
    Component for handling exclusive checkboxes related to specimen parameters.

    Args:
        file_reference (Reactive[SpecimenItem]): Reactive object representing the reference to the specimen item.
        :param sample_controller:
    """

    names = ['Uncorrected', 'Corrected', 'Bulk', 'Mass']
    parameters = [Parameter.TSUSC.value, Parameter.CSUSC.value, Parameter.BSUSC.value, Parameter.MSUSC.value]

    active_checkbox, set_active_checkbox = solara.use_state(
        parameters.index(sample_controller.sample.value.get_y_column()))
    available_checkboxes, set_available_checkboxes = solara.use_state([True] * 4)

    def handle_change(checkbox_id):
        """
        Handle the change event for checkboxes.

        Args:
            checkbox_id (int): The index of the checkbox.
        """
        set_active_checkbox(checkbox_id)

        sample_controller.change_column('y_column', parameters[checkbox_id])

    def check_availability():
        specimen_item = sample_controller.get_selected_specimen_item()
        if specimen_item:
            columns = specimen_item.measurement.value.get_measurement_columns()
            availability = [param in columns for param in parameters]
            set_available_checkboxes(availability)

    solara.use_effect(check_availability, [])

    if sample_controller.get_selected_specimen_item().measurement.value:
        for index, column in enumerate(file_reference.value.measurement.value.get_measurement_columns()):
            if column in parameters:
                index = parameters.index(column)
                solara.Checkbox(
                    label=names[parameters.index(column)],
                    value=(active_checkbox == index),
                    on_value=lambda _, i=index: handle_change(i))

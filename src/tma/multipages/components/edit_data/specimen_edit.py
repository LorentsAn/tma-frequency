import solara
from solara import Reactive

from tma.core.service.sample.controller.sample_controller import SampleController
from tma.core.service.sample.controller.repository_controllers.sample_controller import SampleRepositoryController
from tma.core.service.sample.controller.sample_correction_controller import SampleCorrectionController
from tma.core.service.sample.model.specimen_item import SpecimenItem

"""
This module provides components for editing specimen items and performing various calculations.

Attributes:
    constant_furnace_value (solara.Reactive): Reactive object representing the constant furnace value.
    filename_furnace_value (solara.Reactive): Reactive object representing the filename of the furnace.
    volume_constant_value (solara.Reactive[float]): Reactive object representing the volume constant value.
    mass_constant_value (solara.Reactive[float]): Reactive object representing the mass constant value.
    density_constant_value (solara.Reactive[float]): Reactive object representing the density constant value.
    error_processing_subtraction (solara.Reactive): Reactive object representing the error message for subtraction processing.

"""

constant_furnace_value = solara.reactive(0.0)
filename_furnace_value = solara.reactive('')

volume_constant_value: Reactive[float] = solara.reactive(0.0)
mass_constant_value: Reactive[float] = solara.reactive(0.0)
density_constant_value: Reactive[float] = solara.reactive(0.0)

error_processing_subtraction = solara.reactive('')
error_message = solara.reactive("")


@solara.component
def SpecimenEditBar(sample_controller: SampleController, file_reference: Reactive[SpecimenItem]):
    """
    Component for editing specimen items and performing calculations.

    Args:
        file_reference (Reactive[SpecimenItem]): Reactive object representing the reference to the specimen item.
        :param sample_controller:
    """

    uploaded_files_without_current = solara.reactive(sample_controller.get_empty_source_file_items_plain_list().copy())
    sample_controller_model = SampleRepositoryController(solara.get_session_id())

    calculated_error_message, set_error_message = solara.use_state("")
    sample_correction_controller = SampleCorrectionController(sample_controller)

    def update_uploaded_files():
        new_list = sample_controller.get_empty_source_file_items_plain_list().copy()
        if sample_controller.get_selected_specimen_item().is_empty_source_file:
            new_list.remove(sample_controller.get_selected_specimen_item().filename.value)
        uploaded_files_without_current.set(new_list)

    def correct_by_subtraction_constant(correct_all_files=False):
        error_processing_subtraction.set('')
        error = sample_correction_controller.correct_by_constant(float(constant_furnace_value.value), correct_all_files)
        if error:
            error_processing_subtraction.set(error)

    def correct_by_file(correct_all_files=False):
        error_processing_subtraction.set('')
        error = sample_correction_controller.correct_by_file(filename_furnace_value.value, correct_all_files)
        if error:
            error_processing_subtraction.set(error)

    def create_empty_file(new_filename_value):
        if new_filename_value is None:
            return
        new_item = SpecimenItem.load_from_file(new_filename_value, True, True)
        sample_controller.add_specimen_items([new_item])
        filename_furnace_value.set(new_item.filename.value)
        update_uploaded_files()

    def calculate_bulk_by_volume(calculate_for_all_files=False):
        error = sample_correction_controller.calculate_bulk(
            method='volume', volume=volume_constant_value.value, calculate_for_all_files=calculate_for_all_files)
        set_error_message('')
        if error is not None:
            set_error_message(error)

    def calculate_bulk_by_mass(calculate_for_all_files=False):
        error = sample_correction_controller.calculate_bulk(
            method='mass',
            calculate_for_all_files=calculate_for_all_files,
            mass=mass_constant_value.value,
            density=density_constant_value.value)
        set_error_message('')
        if error is not None:
            set_error_message(error)

    def calculate_mass_susceptibility(calculate_for_all_files=False):
        error = sample_correction_controller.calculate_mass(
            mass_constant_value.value, calculate_for_all_files=calculate_for_all_files)
        set_error_message('')
        if error is not None:
            set_error_message(error)

    def show_data():
        index = sample_controller.on_file_item_select(filename_furnace_value.value)
        if index is None:
            return
        sample_controller_model.update_sample(selected_file_index=index)

        file_reference.set(sample_controller.get_selected_specimen_item())

    open_subtract_file_confirmation = solara.reactive(False)
    open_subtract_constant_confirmation = solara.reactive(False)

    with solara.Card("Empty furnace subtraction"):
        with solara.Column():
            with solara.Row():
                solara.InputFloat("Constant furnace value", value=constant_furnace_value,
                                  continuous_update=True)
                solara.Button("Subtract", on_click=lambda: open_subtract_constant_confirmation.set(True))
                solara.lab.ConfirmationDialog(open_subtract_constant_confirmation,
                                              ok="Ok, Apply", on_ok=lambda: correct_by_subtraction_constant(True),
                                              cancel="Correct only the selected file",
                                              on_cancel=lambda: correct_by_subtraction_constant(False),
                                              content="Apply subtraction to all files? ")
            with solara.Column():
                solara.FileDrop(on_file=create_empty_file,
                                on_total_progress=lambda *args: None,
                                label="Drag new empty file here",
                                lazy=False
                                )
                solara.Select(
                    "Name of empty file source",
                    values=uploaded_files_without_current.value,
                    value=filename_furnace_value
                )
            with solara.Row():
                solara.Button("Open", on_click=show_data)
                solara.Button("Subtract", on_click=lambda: open_subtract_file_confirmation.set(True))
                solara.lab.ConfirmationDialog(open_subtract_file_confirmation,
                                              ok="Ok, Apply", on_ok=lambda: correct_by_file(True),
                                              cancel="Correct only the this one",
                                              on_cancel=lambda: correct_by_file(False),
                                              content="Apply subtraction to all files? ")
            with solara.Row():
                if error_processing_subtraction.value:
                    solara.Error(label=error_processing_subtraction.value)
    with solara.Card("Calculate bulk/mass susceptibility"):
        if calculated_error_message != '':
            solara.Error(label=calculated_error_message)
        with solara.Column():
            calculate_bulk_by_volume_for_all = solara.reactive(False)
            calculate_bulk_by_mass_for_all = solara.reactive(False)
            calculate_mass_for_all = solara.reactive(False)

            with solara.Row():
                solara.InputFloat("Volume (ccm)", value=volume_constant_value, continuous_update=True)
                solara.Button("Calculate bulk", on_click=lambda: calculate_bulk_by_volume_for_all.set(True))
                solara.lab.ConfirmationDialog(calculate_bulk_by_volume_for_all,
                                              ok="Ok, Apply", on_ok=lambda: calculate_bulk_by_volume(True),
                                              cancel="Calculate only this one",
                                              on_cancel=lambda: calculate_bulk_by_volume(False),
                                              content="Apply the calculation to all files of this type? ")
            with solara.Row():
                solara.InputFloat("Mass (g)", value=mass_constant_value, continuous_update=True)
                solara.Button("Calculate mass", on_click=lambda: calculate_mass_for_all.set(True))
                solara.lab.ConfirmationDialog(calculate_mass_for_all,
                                              ok="Ok, Apply", on_ok=lambda: calculate_mass_susceptibility(True),
                                              cancel="Calculate only this one",
                                              on_cancel=lambda: calculate_mass_susceptibility(False),
                                              content="Apply the calculation to all files of this type? ")
            with solara.Row():
                solara.InputFloat("Density (g/ccm)", value=density_constant_value, continuous_update=True)
                solara.Button("Calculate bulk", on_click=lambda: calculate_bulk_by_mass_for_all.set(True))
                solara.lab.ConfirmationDialog(calculate_bulk_by_mass_for_all,
                                              ok="Ok, Apply", on_ok=lambda: calculate_bulk_by_mass(True),
                                              cancel="Calculate only this one",
                                              on_cancel=lambda: calculate_bulk_by_mass(False),
                                              content="Apply the calculation to all files of this type?")
            with solara.Row():
                pass
        # with solara.Row():
        #     solara.InputText("Name", value=solara.reactive(''), continuous_update=True)
        #     solara.Button("Update")

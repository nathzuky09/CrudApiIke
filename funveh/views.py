from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import FuncionarioForm, VehiculoForm
from .models import Funcionario, Vehiculo
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import FuncionarioForm, VehiculoFormSet


# vistas del proyecto 

#Home
def home(request):
    return render(request, 'home.html')
#Registro
def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm()
        })
    else:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tasks')
        else:
            return render(request, 'signup.html', {
                'form': form,
                'error': 'Formulario de registro no válido'
            })

#Control panel
def tasks(request):
    # Obtén todos los funcionarios y vehículos de la base de datos
    funcionarios = Funcionario.objects.all()
    vehiculos = Vehiculo.objects.all()
    
    # Pasa la lista de funcionarios y vehículos al contexto de la plantilla
    return render(request, 'tasks.html', {
        'funcionarios': funcionarios,
        'vehiculos': vehiculos
    })


#Crear registros para la base de datos
def create_task(request):
    if request.method == 'GET':
        # Crea instancias vacías de los formularios para mostrarlas en la plantilla
        funcionario_form = FuncionarioForm()
        vehiculo_form = VehiculoForm()
        
        return render(request, 'create_task.html', {
            'funcionario_form': funcionario_form,
            'vehiculo_form': vehiculo_form
        })
    
    elif request.method == 'POST':
        funcionario_form = FuncionarioForm(request.POST)
        vehiculo_form = VehiculoForm(request.POST)
        
        if funcionario_form.is_valid() and vehiculo_form.is_valid():
            funcionario = funcionario_form.save()
            vehiculo = vehiculo_form.save(commit=False)
            vehiculo.funcionario = funcionario
            vehiculo.save()
            return redirect('tasks')  # Redirige a la vista deseada después de guardar los datos
        else:
            return render(request, 'create_task.html', {
                'funcionario_form': funcionario_form,
                'vehiculo_form': vehiculo_form,
                'error': 'Formulario no válido'
            })


#Detalle de la tarea

def task_detail(request, task_id):
    vehiculo = get_object_or_404(Vehiculo, id=task_id)  # Recupera el vehículo por su ID
    funcionario = vehiculo.funcionario  # Obtiene el funcionario asociado al vehículo
    return render(request, 'task_detail.html', {
        'vehiculo': vehiculo,
        'funcionario': funcionario
    })  # Pasa el vehículo y el funcionario a la plantilla


#Actualizar datos o eliminar
def update_funcionario(request, pk):
    funcionario = get_object_or_404(Funcionario, pk=pk)
    vehiculos = Vehiculo.objects.filter(funcionario=funcionario)
    
    # Crear un formset para los vehículos
    VehiculoFormSet = modelformset_factory(Vehiculo, form=VehiculoForm, extra=0)

    if request.method == 'POST':
        funcionario_form = FuncionarioForm(request.POST, instance=funcionario)
        formset = VehiculoFormSet(request.POST, queryset=vehiculos)
        
        if 'delete' in request.POST:
            # Eliminar funcionario y vehículos asociados
            vehiculos.delete()  # Elimina los vehículos asociados
            funcionario.delete()  # Elimina el funcionario
            messages.success(request, "Funcionario y vehículos eliminados exitosamente.")
            return redirect('tasks')  # Redirige a la página de lista de funcionarios
        
        if funcionario_form.is_valid() and formset.is_valid():
            # Guardar los datos del funcionario
            funcionario_form.save()

            # Guardar y eliminar los vehículos
            for form in formset:
                if form.cleaned_data.get('DELETE'):
                    vehiculo = form.instance
                    vehiculo.delete()
                else:
                    form.save()

            messages.success(request, "Datos actualizados exitosamente.")
            return redirect('tasks')  # Redirige a la página de lista de funcionarios
    else:
        funcionario_form = FuncionarioForm(instance=funcionario)
        formset = VehiculoFormSet(queryset=vehiculos)

    return render(request, 'update_funcionario.html', {
        'funcionario_form': funcionario_form,
        'formset': formset
    })

#Vista para cerrar sesion
        
def cerrar_sesion(request):
    logout(request)
    return redirect('home')

#Vista inicio de sesion
def inicio_sesion(request):
    if request.method == 'GET':
        return render(request, 'inicio_sesion.html', {
            'form': AuthenticationForm()
        })
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('tasks')
            else:
                return render(request, 'inicio_sesion.html', {
                    'form': form,
                    'error': 'Usuario o contraseña incorrectos'
                })
        else:
            return render(request, 'inicio_sesion.html', {
                'form': form,
                'error': 'Formulario no válido'
            })



       
        
    
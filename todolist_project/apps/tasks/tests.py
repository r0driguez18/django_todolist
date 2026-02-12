from django.test import TestCase
from .models import Task
from django.contrib.auth.models import User

class TaskModelTest(TestCase):

    ### inicialização dos testes, criando um user e uma tarefa para os testes subsequentes
    def setUp(self):
        self.user = User.objects.create_user(username='ederlino', email='ederlino.tavares@gmail.com', password='testpass')
        self.task = Task.objects.create(owner=self.user, title='Test Task', description='This is a test task.')

    ### testes para verificar se a criação da tarefa foi bem sucedida 
    def test_task_creation(self):
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.description, 'This is a test task.')
        self.assertFalse(self.task.is_done)
        self.assertEqual(self.task.owner.username, 'ederlino')

    ### verifica se o utilizador autenticado pode estar a visualização da lista de tarefas
    def test_task_list_view(self):
        self.client.login(username='ederlino', password='testpass')
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')
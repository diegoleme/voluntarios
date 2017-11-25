# coding=UTF-8

from django.contrib import admin
from django.contrib.gis.admin import GeoModelAdmin
from django.db import transaction

# Como usar TinyMCE para editar flatpages:
# source: https://stackoverflow.com/questions/15123927/embedding-tinymce-in-django-flatpage
from django.contrib.flatpages.admin import FlatpageForm, FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from tinymce.widgets import TinyMCE

from vol.models import AreaTrabalho, AreaAtuacao, Voluntario, Entidade, Necessidade, AreaInteresse

from vol.views import envia_confirmacao_voluntario, envia_confirmacao_entidade

class MyFlatPageForm(FlatpageForm):

    class Meta:
        model = FlatPage
        fields = FlatpageForm.Meta.fields
        widgets = {
            'content' : TinyMCE(attrs={'cols': 100, 'rows': 15}),
        }


class MyFlatPageAdmin(FlatPageAdmin):
    form = MyFlatPageForm

class AreaTrabalhoAdmin(admin.ModelAdmin):
    pass

class AreaAtuacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'indice')
    fields = ['nome', 'categoria', 'indice', 'id_antigo',]
    readonly_fields = ['id_antigo']

class AreaInteresseInline(admin.TabularInline):
    model = AreaInteresse
    fields = ['area_atuacao',]
    extra = 0

class VoluntarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'data_cadastro', 'importado', 'confirmado', 'aprovado',)
    ordering = ('-confirmado', '-data_cadastro',)
    search_fields = ('nome', 'email', )
    readonly_fields = ('site', 'importado', 'confirmado',)
    actions = ['aprovar', 'enviar_confirmacao']
    inlines = [
        AreaInteresseInline,
    ]

    @transaction.atomic
    def aprovar(self, request, queryset):
        num_updates = 0
        for obj in queryset:
            if not obj.aprovado:
                obj.aprovado = True
                obj.save(update_fields=['aprovado'])
                num_updates = num_updates + 1
        main_msg = ''
        if num_updates > 0:
            main_msg = u'%s voluntário(s) aprovado(s). ' % num_updates
        extra_msg = ''
        total_recs = len(queryset)
        if total_recs > num_updates:
            extra_msg = u'%s não modificado(s) por já estar(em) aprovado(s).' % (total_recs-num_updates)
        self.message_user(request, "%s%s" % (main_msg, extra_msg))
    aprovar.short_description = "Aprovar Voluntários selecionados"

    def enviar_confirmacao(self, request, queryset):
        num_messages = 0
        for obj in queryset:
            if not obj.confirmado:
                envia_confirmacao_voluntario(obj.nome, obj.email)
                num_messages = num_messages + 1
        main_msg = ''
        if num_messages > 0:
            main_msg = u'%s voluntário(s) notificado(s). ' % num_messages
        extra_msg = ''
        total_recs = len(queryset)
        if total_recs > num_messages:
            extra_msg = u'%s não notificado(s) por já possuir(em) cadastro confirmado.' % (total_recs-num_messages)
        self.message_user(request, "%s%s" % (main_msg, extra_msg))
    enviar_confirmacao.short_description = "Enviar nova mensagem de confirmação"

class NecessidadeInline(admin.TabularInline):
    model = Necessidade
    fields = ['qtde_orig', 'descricao', 'valor_orig', 'data_solicitacao',]
    readonly_fields = ['data_solicitacao']
    extra = 0

class EntidadeAdmin(GeoModelAdmin):
    list_display = ('razao_social', 'cnpj', 'email', 'data_cadastro', 'importado', 'confirmado', 'aprovado',)
    ordering = ('-aprovado', '-data_cadastro',)
    search_fields = ('razao_social', 'cnpj', 'email', )
    exclude = ('coordenadas',)
    readonly_fields = ('geocode_status', 'importado', 'confirmado',)
    actions = ['aprovar', 'enviar_confirmacao']
    inlines = [
        NecessidadeInline,
    ]

    @transaction.atomic
    def aprovar(self, request, queryset):
        num_updates = 0
        for obj in queryset:
            if not obj.aprovado:
                obj.aprovado = True
                obj.save(update_fields=['aprovado'])
                num_updates = num_updates + 1
        main_msg = ''
        if num_updates > 0:
            main_msg = u'%s entidade(s) aprovada(s). ' % num_updates
        extra_msg = ''
        total_recs = len(queryset)
        if total_recs > num_updates:
            extra_msg = u'%s não modificada(s) por já estar(em) aprovada(s).' % (total_recs-num_updates)
        self.message_user(request, "%s%s" % (main_msg, extra_msg))
    aprovar.short_description = "Aprovar Entidades selecionadas"

    def enviar_confirmacao(self, request, queryset):
        num_messages = 0
        for obj in queryset:
            if not obj.confirmado:
                envia_confirmacao_entidade(obj.razao_social, obj.email)
                num_messages = num_messages + 1
        main_msg = ''
        if num_messages > 0:
            main_msg = u'%s entidade(s) notificada(s). ' % num_messages
        extra_msg = ''
        total_recs = len(queryset)
        if total_recs > num_messages:
            extra_msg = u'%s não notificada(s) por já possuir(em) cadastro confirmado.' % (total_recs-num_messages)
        self.message_user(request, "%s%s" % (main_msg, extra_msg))
    enviar_confirmacao.short_description = "Enviar nova mensagem de confirmação"

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, MyFlatPageAdmin)
admin.site.register(AreaTrabalho, AreaTrabalhoAdmin)
admin.site.register(AreaAtuacao, AreaAtuacaoAdmin)
admin.site.register(Voluntario, VoluntarioAdmin)
admin.site.register(Entidade, EntidadeAdmin)


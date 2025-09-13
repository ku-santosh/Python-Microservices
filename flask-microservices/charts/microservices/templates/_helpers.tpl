{{- define "microservices.name" -}}
microservices
{{- end -}}

{{- define "microservices.fullname" -}}
{{ include "microservices.name" . }}
{{- end -}}

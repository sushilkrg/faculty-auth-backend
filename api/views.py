# api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Faculty
from .serializers import FacultySerializer

import face_recognition


class FacultyList(APIView):
    
    def get(self, request):
        faculties = Faculty.objects.all()
        serializer = FacultySerializer(faculties, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FacultySerializer(data=request.data)
        if serializer.is_valid():
            image_file = request.FILES.get('image')
            if image_file:
                serializer.validated_data['image'] = image_file
                
                image_data = face_recognition.load_image_file(image_file)
                encoding = face_recognition.face_encodings(image_data)[0]
                serializer.validated_data['face_encoding'] = encoding.tobytes()  # Store encoding as binary data.
                
            faculty = serializer.save()
            return Response(FacultySerializer(faculty).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FacultyDetail(APIView):

    def get_object(self, pk):
        try:
            return Faculty.objects.get(pk=pk)
        except Faculty.DoesNotExist:
            return None

    def get(self, request, pk):
        faculty = self.get_object(pk)
        if faculty is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = FacultySerializer(faculty)
        return Response(serializer.data)

    def put(self, request, pk):
        faculty = self.get_object(pk)
        if faculty is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = FacultySerializer(faculty, data=request.data)
        if serializer.is_valid():
            updated_faculty = serializer.save()
            return Response(FacultySerializer(updated_faculty).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        faculty = self.get_object(pk)
        if faculty is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        faculty.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FaceAuthenticationView(APIView):

    def post(self, request):
        uploaded_image_file = request.FILES.get('image')
        
        if uploaded_image_file is None:
            return Response({"error": "No image provided."}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_image_data = face_recognition.load_image_file(uploaded_image_file)

        try:
            uploaded_encoding = face_recognition.face_encodings(uploaded_image_data)[0]
        except IndexError:
            return Response({"error": "No face detected in the uploaded image."}, status=status.HTTP_400_BAD_REQUEST)

        faculties = Faculty.objects.all()
        
        for faculty in faculties:
            stored_encoding = face_recognition.face_encodings(face_recognition.load_image_file(faculty.image.path))[0]
            
            if face_recognition.compare_faces([stored_encoding], uploaded_encoding)[0]:
                return Response({"message": f"Authenticated: {faculty.name} logged in"}, status=status.HTTP_200_OK)

        return Response({"message": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)

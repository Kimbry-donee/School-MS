    
class BookQuerySet(models.QuerySet):
  def oxford_publisher(self):
    return self.filter(publisher__name='Oxford Unversity Press (T)')
  
  def get_all_book(self):
    return self.all()
    # self.annotate(num_authors=Coalesce(Count("authors"), 0))
  def num_authors_cotrib(self):
    return self.annotate(num_authors=Coalesce(Count("authors"), 0))

class BookManager(models.Manager):
  def get_queryset(self):
    return super().get_queryset().filter(publisher__name='Oxford Unversity Press (T)')

  def num_authors_cotrib(self):
    return self.annotate(num_authors=Coalesce(Count("authors"), 0))



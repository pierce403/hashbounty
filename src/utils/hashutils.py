class SolutionValidator(object):
    def __call__(self, form, field):
        from wtforms.validators import ValidationError
        b = form.bounty
        if b.type == 'md5':
            import md5
            if md5.md5(field.data).hexdigest() != b.hash:
                raise ValidationError(u'Bad solution.')
        elif b.type == 'sha1':
            import hashlib
            if hashlib.sha1(field.data).hexdigest() != b.hash:
                raise ValidationError(u'Bad solution.')

class HashValidator(object):
    def __call__(self, form, field):
        from wtforms.validators import ValidationError
        type = form.type.data
        hash = form.hash.data

        try:
            int(hash, 16)
        except ValueError:
            raise ValidationError(u'Hash must be valid hex string.')

        if type == 'md5':
            if len(hash) != 32:
                raise ValidationError(u'MD5 hash must be 32 characters long.')
        elif type == 'sha1':
            if len(hash) != 40:
                raise ValidationError(u'SHA1 hash must be 40 characters long.')

